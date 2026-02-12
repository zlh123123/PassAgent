"""worker_loop 协程：FIFO 取任务、调 DeepSeek、塞事件"""
import asyncio
import json
from openai import AsyncOpenAI

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from worker.queue import task_queue, ChatTask
from database.connection import SessionLocal
from services.session_service import save_message, get_messages

SYSTEM_PROMPT = """你是 PassAgent，一个基于大语言模型的口令安全智能助手。你可以帮助用户：
1. 评估口令强度
2. 检测口令是否泄露
3. 生成安全且好记的口令
4. 通过记忆片段恢复遗忘的口令
5. 提供口令安全建议

请用中文回复，保持专业且友好的语气。在回复末尾自然地附带 2-3 个引导性建议。"""


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
    )


async def _process_task(task: ChatTask):
    """处理单个聊天任务"""
    task.status = "processing"
    await task.event_queue.put({"event": "task_started", "data": {"task_id": task.task_id}})

    try:
        # Load conversation history from DB
        db = SessionLocal()
        try:
            history = get_messages(db, task.user_id, task.session_id)
        finally:
            db.close()

        # Build messages for DeepSeek
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in history:
            role = "user" if msg["message_type"] == "human" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
        # Add current message
        messages.append({"role": "user", "content": task.message})

        # Save user message to DB
        db = SessionLocal()
        try:
            save_message(db, task.session_id, task.user_id, task.message, "human")
        finally:
            db.close()

        # Call DeepSeek with streaming
        client = _get_client()
        stream = await client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            stream=True,
        )

        full_content = ""
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                await task.event_queue.put({
                    "event": "response_chunk",
                    "data": {"content": content},
                })

        # Save assistant message to DB
        db = SessionLocal()
        try:
            message_id = save_message(
                db, task.session_id, task.user_id, full_content, "assistant"
            )
        finally:
            db.close()

        await task.event_queue.put({
            "event": "response_done",
            "data": {"message_id": message_id},
        })

        task.status = "success"

    except Exception as e:
        task.status = "fail"
        await task.event_queue.put({
            "event": "task_failed",
            "data": {"error": str(e)},
        })

    finally:
        await task.event_queue.put({"event": "done", "data": {}})


async def worker_loop():
    """Worker 主循环，持续从队列取任务处理"""
    while True:
        task = await task_queue.get()
        try:
            await _process_task(task)
        except Exception as e:
            print(f"Worker error: {e}")
        finally:
            task_queue.task_done()
