"""charset_analyze 工具：分析口令字符组成"""
from __future__ import annotations

import string

from agent.graph import register_tool
from agent.state import PassAgentState


def analyze_charset(password: str) -> dict:
    """分析口令的字符组成。"""
    length = len(password)
    if length == 0:
        return {
            "length": 0,
            "has_upper": False,
            "has_lower": False,
            "has_digit": False,
            "has_special": False,
            "charset_size": 0,
            "unique_chars": 0,
            "unique_ratio": 0.0,
            "char_categories": 0,
            "category_detail": {},
        }

    upper_count = sum(1 for c in password if c in string.ascii_uppercase)
    lower_count = sum(1 for c in password if c in string.ascii_lowercase)
    digit_count = sum(1 for c in password if c in string.digits)
    special_count = sum(1 for c in password if c in string.punctuation)
    other_count = length - upper_count - lower_count - digit_count - special_count

    has_upper = upper_count > 0
    has_lower = lower_count > 0
    has_digit = digit_count > 0
    has_special = special_count > 0
    has_other = other_count > 0

    # 有效字符集大小
    charset_size = 0
    if has_upper:
        charset_size += 26
    if has_lower:
        charset_size += 26
    if has_digit:
        charset_size += 10
    if has_special:
        charset_size += 32
    if has_other:
        charset_size += 128

    unique_chars = len(set(password))
    char_categories = sum([has_upper, has_lower, has_digit, has_special])

    return {
        "length": length,
        "has_upper": has_upper,
        "has_lower": has_lower,
        "has_digit": has_digit,
        "has_special": has_special,
        "charset_size": charset_size,
        "unique_chars": unique_chars,
        "unique_ratio": round(unique_chars / length, 2),
        "char_categories": char_categories,
        "category_detail": {
            "uppercase": upper_count,
            "lowercase": lower_count,
            "digits": digit_count,
            "special": special_count,
            "other": other_count,
        },
    }


@register_tool("charset_analyze")
async def charset_analyze_tool(state: PassAgentState) -> dict:
    """分析口令字符组成：长度、大小写、数字、特殊字符、唯一字符比例。"""
    params = state.get("action_params", {})
    password = params.get("password", "")
    return {"_tool_result": analyze_charset(password)}
