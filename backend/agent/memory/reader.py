"""记忆读取：全量偏好/约束 + 语义检索事实 + 访问追踪 + 过期标记"""
from __future__ import annotations

from datetime import datetime, timedelta

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
# 记忆过期天数（超过此天数未访问标记为 stale）
STALE_DAYS = 90


def _now_iso() -> str:
    from utils.timezone import beijing_now_iso
    return beijing_now_iso()


def _is_expired(last_accessed: str | None, created: str | None) -> bool:
    """判断记忆是否超过 STALE_DAYS 天未被访问。"""
    from utils.timezone import beijing_now
    ref = last_accessed or created
    if not ref:
        return False
    try:
        ts = datetime.fromisoformat(ref)
        if ts.tzinfo is None:
            from utils.timezone import BEIJING_TZ
            ts = ts.replace(tzinfo=BEIJING_TZ)
        return beijing_now() - ts > timedelta(days=STALE_DAYS)
    except (ValueError, TypeError):
        return False


def _touch_memories(db: DBSession, memories: list[UserMemory]) -> None:
    """刷新被命中记忆的 last_accessed_at 和 access_count。"""
    now = _now_iso()
    for m in memories:
        m.last_accessed_at = now
        m.access_count = (m.access_count or 0) + 1
        # 被访问后清除 stale 标记
        if m.is_stale:
            m.is_stale = 0
    try:
        db.commit()
    except Exception:
        db.rollback()


def _mark_stale(db: DBSession, memories: list[UserMemory]) -> None:
    """将超期未访问的记忆标记为 is_stale=1。"""
    changed = False
    for m in memories:
        if not m.is_stale and _is_expired(m.last_accessed_at, m.created_at):
            m.is_stale = 1
            changed = True
    if changed:
        try:
            db.commit()
        except Exception:
            db.rollback()


async def retrieve_memory(
    db: DBSession,
    user_id: str,
    query: str,
) -> list[dict]:
    """检索用户记忆。

    策略：
    1. PREFERENCE / CONSTRAINT 类型 → 全量返回（通常数量少，且每次都需要）
    2. FACT 类型 → 语义检索 top-k；若 embedding 不可用则回退到关键词匹配
    3. 命中的记忆刷新 last_accessed_at、access_count += 1
    4. 顺便标记超期未访问的记忆为 stale
    5. stale 记忆会在返回结果中带上标记，供 Agent 主动询问用户确认

    Returns:
        [{"memory_id": ..., "content": ..., "memory_type": ..., "source": ..., "is_stale": ...}, ...]
    """
    all_memories = (
        db.query(UserMemory)
        .filter(UserMemory.user_id == user_id)
        .all()
    )

    if not all_memories:
        return []

    # 顺便标记超期记忆
    _mark_stale(db, all_memories)

    # 1) 全量返回偏好和约束
    results: list[dict] = []
    hit_memories: list[UserMemory] = []
    facts: list[UserMemory] = []

    for m in all_memories:
        if m.memory_type in ("PREFERENCE", "CONSTRAINT"):
            results.append(_to_dict(m))
            hit_memories.append(m)
        else:
            facts.append(m)

    if not facts:
        _touch_memories(db, hit_memories)
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
            hit_memories.append(m)
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
            hit_memories.append(m)

    # 3) 刷新被命中记忆的访问时间
    _touch_memories(db, hit_memories)

    return results


def _to_dict(m: UserMemory) -> dict:
    return {
        "memory_id": m.memory_id,
        "content": m.content,
        "memory_type": m.memory_type,
        "source": m.source or "auto",
        "is_stale": bool(m.is_stale),
    }
