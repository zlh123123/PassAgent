"""basic_analysis 工具：字符组成分析 + 重复/序列检测（合并 charset + repetition）"""
from __future__ import annotations

import re
import string

from agent.graph import register_tool
from agent.state import PassAgentState


# --------------- charset 分析 ---------------

def _analyze_charset(password: str) -> dict:
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


# --------------- repetition 检测 ---------------

def _check_repetition(password: str) -> dict:
    """检测口令中的重复模式。"""
    if not password:
        return {
            "max_repeat_char": 0,
            "repeated_chars": [],
            "repeated_substrings": [],
            "has_sequential": False,
            "sequential_patterns": [],
        }

    # 1) 连续重复字符（如 aaa, 1111）
    repeated_chars: list[dict] = []
    max_repeat = 1
    for m in re.finditer(r"(.)\1{2,}", password):
        run_len = len(m.group())
        max_repeat = max(max_repeat, run_len)
        repeated_chars.append({
            "char": m.group(1),
            "count": run_len,
            "position": m.start(),
        })

    # 2) 重复子串（如 abcabc, passpass）— 长度 >= 2 且重复 >= 2 次
    repeated_substrings: list[dict] = []
    seen_subs: set[str] = set()
    pw_lower = password.lower()
    for sub_len in range(2, len(password) // 2 + 1):
        for i in range(len(password) - sub_len + 1):
            sub = pw_lower[i : i + sub_len]
            if sub in seen_subs:
                continue
            count = pw_lower.count(sub)
            if count >= 2:
                seen_subs.add(sub)
                repeated_substrings.append({
                    "substring": password[i : i + sub_len],
                    "count": count,
                    "length": sub_len,
                })

    # 去掉被更长子串包含的短子串
    repeated_substrings.sort(key=lambda x: x["length"], reverse=True)
    filtered: list[dict] = []
    for item in repeated_substrings:
        s = item["substring"].lower()
        if not any(s in f["substring"].lower() and s != f["substring"].lower() for f in filtered):
            filtered.append(item)
    repeated_substrings = filtered

    # 3) 顺序/逆序序列（abc, 321, cba）
    sequential_patterns: list[dict] = []
    _MIN_SEQ = 3
    i = 0
    while i < len(password) - _MIN_SEQ + 1:
        # 递增
        j = i + 1
        while j < len(password) and ord(password[j]) == ord(password[j - 1]) + 1:
            j += 1
        if j - i >= _MIN_SEQ:
            sequential_patterns.append({
                "pattern": password[i:j],
                "position": i,
                "direction": "ascending",
            })
            i = j
            continue
        # 递减
        j = i + 1
        while j < len(password) and ord(password[j]) == ord(password[j - 1]) - 1:
            j += 1
        if j - i >= _MIN_SEQ:
            sequential_patterns.append({
                "pattern": password[i:j],
                "position": i,
                "direction": "descending",
            })
            i = j
            continue
        i += 1

    return {
        "max_repeat_char": max_repeat,
        "repeated_chars": repeated_chars,
        "repeated_substrings": repeated_substrings,
        "has_sequential": len(sequential_patterns) > 0,
        "sequential_patterns": sequential_patterns,
    }


# --------------- 综合风险评估 ---------------

def _assess_risk(charset: dict, repetition: dict) -> str:
    """综合字符和重复模式评估风险等级。"""
    issues = 0

    # 字符组成维度
    if charset["char_categories"] <= 1:
        issues += 2
    elif charset["char_categories"] == 2:
        issues += 1
    if charset["length"] < 8:
        issues += 2
    if charset["unique_ratio"] < 0.5:
        issues += 1

    # 重复维度
    if repetition["max_repeat_char"] >= 4:
        issues += 2
    elif repetition["repeated_chars"]:
        issues += 1
    if repetition["repeated_substrings"]:
        issues += 1
    if repetition["has_sequential"]:
        issues += 1

    if issues >= 4:
        return "high"
    elif issues >= 2:
        return "medium"
    return "low"


# --------------- 注册工具 ---------------

@register_tool("basic_analysis")
async def basic_analysis_tool(state: PassAgentState) -> dict:
    """分析口令字符组成 + 重复/序列检测。"""
    params = state.get("action_params", {})
    password = params.get("password", "")

    charset = _analyze_charset(password)
    repetition = _check_repetition(password)
    risk = _assess_risk(charset, repetition)

    return {
        "_tool_result": {
            "charset": charset,
            "repetition": repetition,
            "risk_level": risk,
        }
    }
