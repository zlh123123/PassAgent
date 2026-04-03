"""记忆读取：从 markdown 记忆档案中提取结构化记忆。"""
from __future__ import annotations

import re

from sqlalchemy.orm import Session as DBSession

from agent.memory.profile import (
    ensure_memory_profile,
    parse_memory_profile,
    touch_memory_profile,
)

TOP_K = 8


def _query_terms(text: str) -> tuple[set[str], set[str]]:
    lowered = (text or "").lower()
    english = set(re.findall(r"[a-z0-9]{2,}", lowered))
    chinese = set(re.findall(r"[\u4e00-\u9fff]", lowered))
    return english, chinese


def _score_fact(query: str, content: str) -> int:
    query_lower = (query or "").strip().lower()
    content_lower = (content or "").lower()
    if not query_lower or not content_lower:
        return 0

    score = 0
    if query_lower in content_lower or content_lower in query_lower:
        score += 4

    query_en, query_zh = _query_terms(query_lower)
    content_en, content_zh = _query_terms(content_lower)
    score += len(query_en & content_en) * 2
    score += len(query_zh & content_zh)
    return score


def _to_dict(content: str, memory_type: str) -> dict:
    return {
        "content": content,
        "memory_type": memory_type,
        "is_stale": False,
    }


async def retrieve_memory(
    db: DBSession,
    user_id: str,
    query: str,
) -> list[dict]:
    """检索用户记忆。

    当前策略：
    - 偏好 / 约束始终全量返回
    - 事实优先按关键词粗排；若事实很少则直接全量返回
    - 文档级记录 last_used_at，避免单条阈值与访问计数
    """
    profile = ensure_memory_profile(db, user_id)
    sections, _ = parse_memory_profile(profile.content_md)

    prefs = sections["PREFERENCE"]
    facts = sections["FACT"]
    constraints = sections["CONSTRAINT"]

    results = [_to_dict(item, "PREFERENCE") for item in prefs]
    results.extend(_to_dict(item, "CONSTRAINT") for item in constraints)

    if not facts:
        if results:
            touch_memory_profile(db, profile)
        return results

    if not query.strip() or len(facts) <= 6:
        selected_facts = facts
    else:
        scored_facts = [(_score_fact(query, content), content) for content in facts]
        scored_facts.sort(key=lambda item: item[0], reverse=True)
        selected_facts = [content for score, content in scored_facts if score > 0][:TOP_K]

    results.extend(_to_dict(item, "FACT") for item in selected_facts)

    if results:
        touch_memory_profile(db, profile)

    return results
