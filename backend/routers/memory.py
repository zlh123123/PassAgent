"""记忆路由"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from database.connection import get_db
from database.models import User, UserMemory
from utils.deps import get_current_user
from schemas.memory import (
    MemoriesListResponse,
    MemoryResponse,
    CreateMemoryRequest,
    CreateMemoryResponse,
)
from agent.memory.embedding import get_embedding, embedding_to_bytes

router = APIRouter(prefix="/api/memories", tags=["memories"])


@router.get("", response_model=MemoriesListResponse)
def list_memories(
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    memories = (
        db.query(UserMemory)
        .filter(UserMemory.user_id == user.user_id)
        .order_by(UserMemory.created_at.desc())
        .all()
    )
    return MemoriesListResponse(
        memories=[
            MemoryResponse(
                memory_id=m.memory_id,
                content=m.content,
                memory_type=m.memory_type,
                source=m.source or "auto",
                created_at=m.created_at or "",
            )
            for m in memories
        ]
    )


@router.post("", response_model=CreateMemoryResponse)
async def create_memory(
    body: CreateMemoryRequest,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    if body.memory_type not in ("PREFERENCE", "FACT", "CONSTRAINT"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="memory_type 必须是 PREFERENCE / FACT / CONSTRAINT",
        )
    memory_id = str(uuid.uuid4())

    # 生成 embedding 向量，失败不阻塞
    vec = await get_embedding(body.content)
    emb_bytes = embedding_to_bytes(vec) if vec else None

    memory = UserMemory(
        memory_id=memory_id,
        user_id=user.user_id,
        content=body.content,
        memory_type=body.memory_type,
        source="manual",
        embedding=emb_bytes,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(memory)
    db.commit()
    return CreateMemoryResponse(memory_id=memory_id, message="记忆已添加")


@router.delete("/{memory_id}")
def delete_memory(
    memory_id: str,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    memory = (
        db.query(UserMemory)
        .filter(UserMemory.memory_id == memory_id, UserMemory.user_id == user.user_id)
        .first()
    )
    if not memory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="记忆不存在")
    db.delete(memory)
    db.commit()
    return {"message": "已删除"}
