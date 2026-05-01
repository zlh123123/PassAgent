"""记忆读取：从 markdown 记忆档案中提取结构化记忆。"""
from __future__ import annotations

import re

from sqlalchemy.orm import Session as DBSession

from agent.memory.profile import (
    ensure_memory_profile,
    parse_memory_profile,
    touch_memory_profile,
)

TOP_K_FACTS = 6
TOP_K_AUTO_PREFERENCES = 3
TOP_K_AUTO_CONSTRAINTS = 3
MANUAL_FACT_BONUS = 3


def _query_terms(text: str) -> tuple[set[str], set[str]]:
    lowered = (text or "").lower()
    english = set(re.findall(r"[a-z0-9]{2,}", lowered))
    chinese = set(re.findall(r"[\u4e00-\u9fff]", lowered))
    return english, chinese


def _base_score(query: str, content: str) -> int:
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


def _to_dict(content: str, memory_type: str, source: str) -> dict:
    return {
        "content": content,
        "memory_type": memory_type,
        "source": source,
        "is_stale": False,
    }


def _select_auto_items(
    items: list[str],
    query: str,
    memory_type: str,
    top_k: int,
) -> list[dict]:
    if not items:
        return []

    query = (query or "").strip()
    if not query:
        return [_to_dict(item, memory_type, "AUTO") for item in items[:top_k]]

    ranked = sorted(
        enumerate(items),
        key=lambda pair: (_base_score(query, pair[1]), pair[0]),
        reverse=True,
    )
    return [
        _to_dict(item, memory_type, "AUTO")
        for _, item in ranked[:top_k]
    ]


async def retrieve_memory(
    db: DBSession,
    user_id: str,
    query: str,
) -> list[dict]:
    """检索用户记忆。

    当前策略：
    - 手动偏好 / 手动约束始终返回
    - 自动偏好 / 自动约束按 query 粗排，最多各返回 3 条
    - 事实统一按关键词粗排；query 为空或无关时不返回事实
    """
    profile = ensure_memory_profile(db, user_id)
    sections, _ = parse_memory_profile(profile.content_md)

    results: list[dict] = []
    query = (query or "").strip()

    for item in sections["MANUAL"]["PREFERENCE"]:
        results.append(_to_dict(item, "PREFERENCE", "MANUAL"))
    for item in sections["MANUAL"]["CONSTRAINT"]:
        results.append(_to_dict(item, "CONSTRAINT", "MANUAL"))

    results.extend(
        _select_auto_items(
            sections["AUTO"]["PREFERENCE"],
            query,
            "PREFERENCE",
            TOP_K_AUTO_PREFERENCES,
        )
    )
    results.extend(
        _select_auto_items(
            sections["AUTO"]["CONSTRAINT"],
            query,
            "CONSTRAINT",
            TOP_K_AUTO_CONSTRAINTS,
        )
    )

    if query:
        fact_candidates: list[tuple[int, int, str, str]] = []
        for source, bonus in (("MANUAL", MANUAL_FACT_BONUS), ("AUTO", 0)):
            for index, content in enumerate(sections[source]["FACT"]):
                score = _base_score(query, content) + bonus
                if score <= bonus:
                    continue
                fact_candidates.append((score, index, source, content))

        fact_candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
        for _, _, source, content in fact_candidates[:TOP_K_FACTS]:
            results.append(_to_dict(content, "FACT", source))

    if results:
        touch_memory_profile(db, profile)

    return results
