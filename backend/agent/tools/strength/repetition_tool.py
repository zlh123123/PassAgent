"""repetition_check 工具：检测口令中的重复字符和序列"""
from __future__ import annotations

import re

from agent.graph import register_tool
from agent.state import PassAgentState


def check_repetition(password: str) -> dict:
    """检测口令中的重复模式。"""
    if not password:
        return {
            "max_repeat_char": 0,
            "repeated_chars": [],
            "repeated_substrings": [],
            "has_sequential": False,
            "sequential_patterns": [],
            "risk_level": "low",
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

    # 风险评估
    issues = len(repeated_chars) + len(repeated_substrings) + len(sequential_patterns)
    covered = set()
    for rc in repeated_chars:
        for k in range(rc["position"], rc["position"] + rc["count"]):
            covered.add(k)
    for sp in sequential_patterns:
        for k in range(sp["position"], sp["position"] + len(sp["pattern"])):
            covered.add(k)
    coverage = len(covered) / len(password) if password else 0

    risk = "high" if coverage > 0.5 or max_repeat >= 4 else "medium" if issues >= 2 else "low"

    return {
        "max_repeat_char": max_repeat,
        "repeated_chars": repeated_chars,
        "repeated_substrings": repeated_substrings,
        "has_sequential": len(sequential_patterns) > 0,
        "sequential_patterns": sequential_patterns,
        "risk_level": risk,
    }


@register_tool("repetition_check")
async def repetition_check_tool(state: PassAgentState) -> dict:
    """检测口令中的重复字符和序列。"""
    params = state.get("action_params", {})
    password = params.get("password", "")
    return {"_tool_result": check_repetition(password)}
