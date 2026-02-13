"""记忆读取：全量偏好/约束 + 语义检索事实"""
from __future__ import annotations

from sqlalchemy.orm import Session as DBSession

from database.models import UserMemory
from agent.memory.embedding import (
    get_embedding,
    bytes_to_embedding,
    cosine_similarity,
)

# 语义检索返回的最大 FACT 条数
TOP_K = 5
# 相似度阈值，低于此值不返回
SIMILARITY_THRESHOLD = 0.3


async def retrieve_memory(
    db: DBSession,
    user_id: str,
    query: str,
) -> list[dict]:
    """检索用户记忆。

    策略：
    1. PREFERENCE / CONSTRAINT 类型 → 全量返回（通常数量少，且每次都需要）
    2. FACT 类型 → 语义检索 top-k；若 embedding 不可用则回退到关键词匹配

    Returns:
        [{"memory_id": ..., "content": ..., "memory_type": ..., "source": ...}, ...]
    """
    all_memories = (
        db.query(UserMemory)
        .filter(UserMemory.user_id == user_id)
        .all()
    )

    if not all_memories:
        return []

    # 1) 全量返回偏好和约束
    results: list[dict] = []
    facts: list[UserMemory] = []

    for m in all_memories:
        if m.memory_type in ("PREFERENCE", "CONSTRAINT"):
            results.append(_to_dict(m))
        else:
            facts.append(m)

    if not facts:
        return results

    # 2) 对 FACT 做语义检索
    query_vec = await get_embedding(query)

    if query_vec is not None:
        # 向量检索
        scored: list[tuple[float, UserMemory]] = []
        for m in facts:
            if m.embedding:
                mem_vec = bytes_to_embedding(m.embedding)
                score = cosine_similarity(query_vec, mem_vec)
                if score >= SIMILARITY_THRESHOLD:
                    scored.append((score, m))
        scored.sort(key=lambda x: x[0], reverse=True)
        for _, m in scored[:TOP_K]:
            results.append(_to_dict(m))
    else:
        # embedding 不可用，回退到关键词匹配
        query_lower = query.lower()
        keywords = query_lower.split()
        matched: list[UserMemory] = []
        for m in facts:
            content_lower = (m.content or "").lower()
            if any(kw in content_lower for kw in keywords):
                matched.append(m)
        for m in matched[:TOP_K]:
            results.append(_to_dict(m))

    return results


def _to_dict(m: UserMemory) -> dict:
    return {
        "memory_id": m.memory_id,
        "content": m.content,
        "memory_type": m.memory_type,
        "source": m.source or "auto",
    }
