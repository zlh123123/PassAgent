"""记忆路由"""
import logging
import uuid
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
from agent.memory.embedding import (
    get_embedding,
    embedding_to_bytes,
    bytes_to_embedding,
    cosine_similarity,
)
from agent.memory.writer import (
    DEDUP_THRESHOLD,
    CONFLICT_THRESHOLD,
    MAX_MEMORIES_PER_USER,
    _evict_lru,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/memories", tags=["memories"])


def _now_iso() -> str:
    from utils.timezone import beijing_now_iso
    return beijing_now_iso()


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
                is_stale=bool(m.is_stale),
                access_count=m.access_count or 0,
                last_accessed_at=m.last_accessed_at,
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

    now = _now_iso()

    # 生成 embedding 向量
    vec = await get_embedding(body.content)
    emb_bytes = embedding_to_bytes(vec) if vec else None

    # 语义冲突检测（与 writer 逻辑一致）
    if vec is not None:
        same_type_memories = (
            db.query(UserMemory)
            .filter(
                UserMemory.user_id == user.user_id,
                UserMemory.memory_type == body.memory_type,
            )
            .all()
        )
        best_sim = 0.0
        best_mem = None
        for m in same_type_memories:
            if m.embedding:
                mem_vec = bytes_to_embedding(m.embedding)
                sim = cosine_similarity(vec, mem_vec)
                if sim > best_sim:
                    best_sim = sim
                    best_mem = m

        if best_sim > DEDUP_THRESHOLD:
            # 重复，不写入
            return CreateMemoryResponse(
                memory_id=best_mem.memory_id if best_mem else "",
                message="已存在相似记忆，无需重复添加",
            )

        if best_sim > CONFLICT_THRESHOLD and best_mem is not None:
            # 冲突替换
            logger.info("手动记忆冲突替换: '%s' → '%s'", best_mem.content, body.content)
            best_mem.content = body.content
            best_mem.embedding = emb_bytes
            best_mem.created_at = now
            best_mem.last_accessed_at = now
            best_mem.access_count = 0
            best_mem.is_stale = 0
            best_mem.source = "manual"
            db.commit()
            return CreateMemoryResponse(memory_id=best_mem.memory_id, message="已更新冲突记忆")

    # 正常新增
    memory_id = str(uuid.uuid4())
    memory = UserMemory(
        memory_id=memory_id,
        user_id=user.user_id,
        content=body.content,
        memory_type=body.memory_type,
        source="manual",
        embedding=emb_bytes,
        access_count=0,
        is_stale=0,
        last_accessed_at=now,
        created_at=now,
    )
    db.add(memory)
    _evict_lru(db, user.user_id)
    db.commit()
    return CreateMemoryResponse(memory_id=memory_id, message="记忆已添加")


@router.delete("")
def delete_all_memories(
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    db.query(UserMemory).filter(UserMemory.user_id == user.user_id).delete()
    db.commit()
    return {"message": "已清除全部记忆"}


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
