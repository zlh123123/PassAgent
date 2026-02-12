"""对话路由：POST /api/chat/{session_id} → SSE"""
import uuid
import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DBSession

from database.connection import get_db
from database.models import User, Session
from utils.deps import get_current_user
from schemas.chat import ChatRequest
from worker.queue import ChatTask, task_queue, active_tasks

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _sse_format(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/{session_id}")
async def chat(
    session_id: str,
    body: ChatRequest,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    # Verify session belongs to user
    session = (
        db.query(Session)
        .filter(Session.session_id == session_id, Session.user_id == user.user_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    # Create task
    task_id = str(uuid.uuid4())
    task = ChatTask(
        task_id=task_id,
        user_id=user.user_id,
        session_id=session_id,
        message=body.message,
        file_ids=body.file_ids,
    )

    # Check queue capacity
    if task_queue.full():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="服务繁忙，请稍后重试",
        )

    position = task_queue.qsize()
    active_tasks[task_id] = task
    await task_queue.put(task)

    async def event_stream():
        try:
            # Send queued event
            yield _sse_format("task_queued", {"task_id": task_id, "position": position})

            # Stream events from task's queue
            while True:
                event = await task.event_queue.get()
                event_type = event["event"]
                event_data = event["data"]
                yield _sse_format(event_type, event_data)

                if event_type == "done":
                    break
        finally:
            active_tasks.pop(task_id, None)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
