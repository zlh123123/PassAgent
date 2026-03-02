"""fragment_combine 工具：将记忆片段排列组合生成候选口令

功能：
1. 对用户提供的片段进行排列组合
2. 自动检测日期类片段并展开为多种格式变体
3. 常见分隔符拼接
"""
from __future__ import annotations

import itertools
import re

from agent.graph import register_tool
from agent.state import PassAgentState

# 常见分隔符
_SEPARATORS = ["", ".", "-", "_", "@", "#"]

# 日期格式模板
_DATE_FORMATS = [
    "{y}{m:02d}{d:02d}",          # 20190101
    "{y}{m}{d}",                   # 201911 (short)
    "{d:02d}{m:02d}{y}",          # 01012019
    "{m:02d}{d:02d}{y}",          # 01012019
    "{y}-{m:02d}-{d:02d}",       # 2019-01-01
    "{d:02d}/{m:02d}/{y}",       # 01/01/2019
    "{m:02d}.{d:02d}.{y}",       # 01.01.2019
    "{y2}{m:02d}{d:02d}",        # 190101
    "{m:02d}{d:02d}",            # 0101
    "{y}",                        # 2019
    "{y2}",                       # 19
    "{d:02d}{m:02d}",            # 0101
]

# 年份正则
_YEAR_RE = re.compile(r"^(19|20)\d{2}$")


def _is_year(fragment: str) -> bool:
    return bool(_YEAR_RE.match(fragment.strip()))


def _expand_year(year_str: str) -> list[str]:
    """将年份扩展为多种日期格式变体。"""
    y = int(year_str)
    y2 = y % 100
    variants: list[str] = [year_str, str(y2)]

    # 为常见月日组合生成变体
    common_dates = [
        (1, 1), (1, 14), (2, 14), (5, 1), (5, 20),
        (6, 1), (7, 1), (8, 15), (10, 1), (12, 25),
    ]
    for m, d in common_dates:
        for fmt in _DATE_FORMATS:
            try:
                v = fmt.format(y=y, y2=y2, m=m, d=d)
                if v not in variants:
                    variants.append(v)
            except (KeyError, ValueError):
                continue

    return variants


def _expand_date_fragments(fragments: list[str]) -> list[str]:
    """检测片段中的年份并展开，非年份片段原样返回。"""
    result: list[str] = []
    for f in fragments:
        if _is_year(f):
            result.extend(_expand_year(f))
        else:
            result.append(f)
    return result


def combine_fragments(
    fragments: list[str],
    pattern: str | None = None,
    max_candidates: int = 200,
) -> dict:
    """排列组合记忆片段生成候选口令。"""
    if not fragments:
        return {"candidates": [], "count": 0}

    # 展开日期片段
    expanded = _expand_date_fragments(fragments)

    candidates: list[str] = []
    seen: set[str] = set()

    def _add(pw: str):
        if pw and pw not in seen and len(pw) >= 4:
            seen.add(pw)
            candidates.append(pw)

    # 1) 直接拼接所有片段（各种分隔符）
    for sep in _SEPARATORS:
        _add(sep.join(fragments))

    # 2) 排列组合（2-4 个片段的全排列）
    unique_frags = list(dict.fromkeys(expanded))  # 去重保序
    for r in range(2, min(len(unique_frags) + 1, 5)):
        for perm in itertools.permutations(unique_frags, r):
            if len(candidates) >= max_candidates:
                break
            for sep in _SEPARATORS[:3]:  # 只用前 3 种分隔符避免爆炸
                _add(sep.join(perm))

    # 3) 两两组合（所有 expanded 片段的笛卡尔积）
    if len(unique_frags) <= 10:
        for a, b in itertools.product(unique_frags, repeat=2):
            if a == b:
                continue
            if len(candidates) >= max_candidates:
                break
            _add(a + b)

    return {
        "candidates": candidates[:max_candidates],
        "count": min(len(candidates), max_candidates),
        "original_fragments": fragments,
        "expanded_fragments": unique_frags[:20],
    }


@register_tool("fragment_combine")
async def fragment_combine_tool(state: PassAgentState) -> dict:
    """将记忆片段排列组合，生成候选口令。"""
    params = state.get("action_params", {})
    fragments = params.get("fragments", [])
    pattern = params.get("pattern")

    result = combine_fragments(fragments, pattern)
    return {"_tool_result": result}
