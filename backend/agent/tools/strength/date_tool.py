"""date_pattern_check 工具：检测口令中的日期模式"""
from __future__ import annotations

import re

from agent.graph import register_tool
from agent.state import PassAgentState

# 日期正则：覆盖常见格式，按长度从长到短排列以优先匹配
_DATE_PATTERNS: list[tuple[str, str]] = [
    # YYYYMMDD / YYYY-MM-DD / YYYY/MM/DD / YYYY.MM.DD
    (r"((?:19|20)\d{2})[-/.]?(0[1-9]|1[0-2])[-/.]?(0[1-9]|[12]\d|3[01])", "YYYY-MM-DD"),
    # DDMMYYYY / DD-MM-YYYY
    (r"(0[1-9]|[12]\d|3[01])[-/.]?(0[1-9]|1[0-2])[-/.]?((?:19|20)\d{2})", "DD-MM-YYYY"),
    # MMDDYYYY / MM-DD-YYYY
    (r"(0[1-9]|1[0-2])[-/.]?(0[1-9]|[12]\d|3[01])[-/.]?((?:19|20)\d{2})", "MM-DD-YYYY"),
    # YYMMDD（6位紧凑）
    (r"(\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])", "YYMMDD"),
    # 纯年份 4 位
    (r"((?:19|20)\d{2})", "YYYY"),
    # MMDD（4位月日）
    (r"(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])", "MMDD"),
]


def _validate_date(year: int, month: int, day: int) -> bool:
    """简单校验日期合理性。"""
    if month < 1 or month > 12 or day < 1:
        return False
    days_in_month = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return day <= days_in_month[month]


def check_date_patterns(password: str) -> dict:
    """检测口令中的日期模式。"""
    if not password:
        return {"has_date": False, "date_patterns": [], "risk_level": "low"}

    found: list[dict] = []
    used_spans: list[tuple[int, int]] = []

    for pattern_re, fmt in _DATE_PATTERNS:
        for m in re.finditer(pattern_re, password):
            start, end = m.start(), m.end()

            # 跳过已被更长模式覆盖的区间
            if any(s <= start and end <= e for s, e in used_spans):
                continue

            groups = m.groups()

            # 验证日期合理性
            valid = True
            if fmt == "YYYY-MM-DD" and len(groups) == 3:
                valid = _validate_date(int(groups[0]), int(groups[1]), int(groups[2]))
            elif fmt == "DD-MM-YYYY" and len(groups) == 3:
                valid = _validate_date(int(groups[2]), int(groups[1]), int(groups[0]))
            elif fmt == "MM-DD-YYYY" and len(groups) == 3:
                valid = _validate_date(int(groups[2]), int(groups[0]), int(groups[1]))

            if not valid:
                continue

            # 短模式只在口令较短时报告
            if fmt in ("YYYY", "MMDD") and len(password) > 12:
                continue

            found.append({
                "matched": m.group(),
                "format": fmt,
                "position": start,
                "length": end - start,
            })
            used_spans.append((start, end))

    # 按长度降序去重，优先保留长匹配
    found.sort(key=lambda x: x["length"], reverse=True)
    final: list[dict] = []
    final_spans: list[tuple[int, int]] = []
    for item in found:
        s, e = item["position"], item["position"] + item["length"]
        if not any(fs <= s and e <= fe for fs, fe in final_spans):
            final.append(item)
            final_spans.append((s, e))

    coverage = 0.0
    if password and final:
        covered = set()
        for item in final:
            for k in range(item["position"], item["position"] + item["length"]):
                covered.add(k)
        coverage = len(covered) / len(password)

    risk = "high" if coverage > 0.5 else "medium" if final else "low"

    return {
        "has_date": len(final) > 0,
        "date_patterns": final,
        "risk_level": risk,
    }


@register_tool("date_pattern_check")
async def date_pattern_check_tool(state: PassAgentState) -> dict:
    """检测口令中的日期模式。"""
    params = state.get("action_params", {})
    password = params.get("password", "")
    return {"_tool_result": check_date_patterns(password)}
