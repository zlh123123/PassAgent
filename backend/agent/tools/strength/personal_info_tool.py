"""personal_info_check 工具：结合用户记忆检测口令中是否包含个人信息"""
from __future__ import annotations

import re

from agent.graph import register_tool
from agent.state import PassAgentState

# 常见 leet speak 映射（反向：从 leet 还原为字母）
_LEET_MAP = {
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s",
    "7": "t", "8": "b", "@": "a", "$": "s", "!": "i",
}


def _normalize(text: str) -> str:
    """将文本标准化：小写 + leet speak 还原。"""
    result = []
    for c in text.lower():
        result.append(_LEET_MAP.get(c, c))
    return "".join(result)


def _extract_keywords_from_memory(memory: dict) -> list[str]:
    """从单条记忆中提取可匹配的关键词。"""
    content = memory.get("content", "")
    if not content:
        return []

    keywords: list[str] = []

    # 提取中文词（2字以上）
    for m in re.finditer(r"[\u4e00-\u9fff]{2,}", content):
        keywords.append(m.group())

    # 提取英文单词（2字母以上）
    for m in re.finditer(r"[a-zA-Z]{2,}", content):
        keywords.append(m.group().lower())

    # 提取数字串（3位以上）
    for m in re.finditer(r"\d{3,}", content):
        keywords.append(m.group())

    # 提取日期
    for m in re.finditer(r"\d{4}[-/.]?\d{2}[-/.]?\d{2}", content):
        # 保留原始和去分隔符两种形式
        keywords.append(m.group())
        keywords.append(re.sub(r"[-/.]", "", m.group()))

    return list(set(keywords))


def check_personal_info(password: str, memories: list[dict] | None = None) -> dict:
    """检测口令中是否包含用户个人信息。"""
    if not password or not memories:
        return {
            "contains_personal_info": False,
            "matched_items": [],
            "risk_level": "low",
        }

    pw_lower = password.lower()
    pw_normalized = _normalize(password)

    matched_items: list[dict] = []
    seen: set[str] = set()

    for mem in memories:
        keywords = _extract_keywords_from_memory(mem)
        memory_type = mem.get("memory_type", "FACT")

        for kw in keywords:
            if len(kw) < 2:
                continue
            kw_lower = kw.lower()
            kw_normalized = _normalize(kw)

            if kw_lower in seen:
                continue

            # 直接匹配
            if kw_lower in pw_lower:
                seen.add(kw_lower)
                matched_items.append({
                    "keyword": kw,
                    "match_type": "exact",
                    "memory_type": memory_type,
                    "memory_content": mem.get("content", "")[:50],
                })
            # leet speak 还原后匹配
            elif len(kw_normalized) >= 3 and kw_normalized in pw_normalized:
                seen.add(kw_lower)
                matched_items.append({
                    "keyword": kw,
                    "match_type": "leet_speak",
                    "memory_type": memory_type,
                    "memory_content": mem.get("content", "")[:50],
                })

    has_match = len(matched_items) > 0
    risk = "high" if len(matched_items) >= 2 else "medium" if has_match else "low"

    return {
        "contains_personal_info": has_match,
        "matched_items": matched_items,
        "risk_level": risk,
    }


@register_tool("personal_info_check")
async def personal_info_check_tool(state: PassAgentState) -> dict:
    """结合用户记忆检测口令中是否包含个人信息。"""
    params = state.get("action_params", {})
    password = params.get("password", "")
    memories = params.get("memories") or state.get("memories") or []
    return {"_tool_result": check_personal_info(password, memories)}
