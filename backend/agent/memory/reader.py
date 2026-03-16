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
TOP_K = 8
# 相似度阈值，低于此值不返回
SIMILARITY_THRESHOLD = 0.45
# PREFERENCE/CONSTRAINT 的相关性过滤阈值（更宽松）；条数少时全量返回
PREF_SIMILARITY_THRESHOLD = 0.25
PREF_FULL_RETURN_LIMIT = 8   # 偏好/约束总数 ≤ 此值时全量返回
PREF_TOP_K = 12              # 超过上限时按相关性取 top-k
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
    1. 先获取 query embedding
    2. PREFERENCE / CONSTRAINT：
       - 总数 ≤ PREF_FULL_RETURN_LIMIT 时全量返回
       - 超过时按语义相关性过滤（阈值 PREF_SIMILARITY_THRESHOLD），取 top PREF_TOP_K
    3. FACT：语义检索 top-k（阈值 SIMILARITY_THRESHOLD）；embedding 不可用回退关键词匹配
    4. 命中的记忆刷新 last_accessed_at、access_count += 1
    5. 顺便标记超期未访问的记忆为 stale
    6. stale 记忆在返回结果中带上标记，供 Agent 主动询问用户确认

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

    # 先获取 query embedding（偏好过滤和事实检索共用）
    query_vec = await get_embedding(query)

    results: list[dict] = []
    hit_memories: list[UserMemory] = []
    facts: list[UserMemory] = []
    prefs_constraints: list[UserMemory] = []

    for m in all_memories:
        if m.memory_type in ("PREFERENCE", "CONSTRAINT"):
            prefs_constraints.append(m)
        else:
            facts.append(m)

    # 1) 偏好和约束：少量全量返回，多量按相关性过滤
    if len(prefs_constraints) <= PREF_FULL_RETURN_LIMIT or query_vec is None:
        for m in prefs_constraints:
            results.append(_to_dict(m))
            hit_memories.append(m)
    else:
        scored_pc: list[tuple[float, UserMemory]] = []
        for m in prefs_constraints:
            if m.embedding:
                mem_vec = bytes_to_embedding(m.embedding)
                score = cosine_similarity(query_vec, mem_vec)
                if score >= PREF_SIMILARITY_THRESHOLD:
                    scored_pc.append((score, m))
            else:
                # 无 embedding 的偏好/约束始终保留
                results.append(_to_dict(m))
                hit_memories.append(m)
        scored_pc.sort(key=lambda x: x[0], reverse=True)
        for _, m in scored_pc[:PREF_TOP_K]:
            results.append(_to_dict(m))
            hit_memories.append(m)

    if not facts:
        _touch_memories(db, hit_memories)
        return results

    # 2) 对 FACT 做语义检索
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
        # embedding 不可用，回退到关键词匹配（按字符级别支持中文）
        query_chars = set(query.replace(" ", ""))
        matched: list[UserMemory] = []
        for m in facts:
            content = m.content or ""
            # 子串匹配或字符集交集
            if query.lower() in content.lower() or len(query_chars & set(content)) >= 2:
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
