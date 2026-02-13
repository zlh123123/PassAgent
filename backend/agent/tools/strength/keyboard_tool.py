"""keyboard_pattern_check 工具：检测口令中的键盘连续模式"""
from __future__ import annotations

from agent.graph import register_tool
from agent.state import PassAgentState

# 常见键盘行布局（QWERTY）
_ROWS = [
    "1234567890",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
]

# 数字键盘
_NUMPAD = [
    "789",
    "456",
    "123",
    "0",
]

# 最小连续长度才算 pattern
_MIN_SEQ_LEN = 3


def _find_sequences(password: str, layout: list[str], min_len: int) -> list[dict]:
    """在给定键盘布局中查找连续按键序列（正向和反向）。"""
    pw_lower = password.lower()
    found: list[dict] = []

    for row in layout:
        row_len = len(row)
        if row_len < min_len:
            continue

        # 正向和反向都检查
        for seq_source, direction in [(row, "forward"), (row[::-1], "reverse")]:
            i = 0
            while i < len(pw_lower):
                # 尝试从 pw_lower[i] 开始匹配 seq_source 中的连续子串
                j = seq_source.find(pw_lower[i])
                if j == -1:
                    i += 1
                    continue

                # 往后延伸匹配
                match_len = 0
                while (
                    i + match_len < len(pw_lower)
                    and j + match_len < len(seq_source)
                    and pw_lower[i + match_len] == seq_source[j + match_len]
                ):
                    match_len += 1

                if match_len >= min_len:
                    found.append({
                        "pattern": password[i : i + match_len],
                        "position": i,
                        "length": match_len,
                        "direction": direction,
                        "row": seq_source if direction == "forward" else seq_source[::-1],
                    })
                    i += match_len
                else:
                    i += 1

    return found


def _find_adjacent_patterns(password: str) -> list[dict]:
    """检测跨行的相邻键模式（如 qaz, wsx, 1qaz）。"""
    # 构建坐标映射
    key_pos: dict[str, tuple[int, int]] = {}
    for r, row in enumerate(_ROWS):
        for c, ch in enumerate(row):
            key_pos[ch] = (r, c)

    pw_lower = password.lower()
    found: list[dict] = []
    i = 0

    while i < len(pw_lower) - _MIN_SEQ_LEN + 1:
        if pw_lower[i] not in key_pos:
            i += 1
            continue

        seq_len = 1
        for k in range(i + 1, len(pw_lower)):
            if pw_lower[k] not in key_pos:
                break
            prev = key_pos[pw_lower[k - 1]]
            curr = key_pos[pw_lower[k]]
            row_diff = abs(curr[0] - prev[0])
            col_diff = abs(curr[1] - prev[1])
            # 相邻键：行差 ≤1 且列差 ≤1，但不能完全相同
            if row_diff <= 1 and col_diff <= 1 and (row_diff + col_diff) > 0:
                seq_len += 1
            else:
                break

        if seq_len >= _MIN_SEQ_LEN:
            found.append({
                "pattern": password[i : i + seq_len],
                "position": i,
                "length": seq_len,
                "direction": "adjacent",
            })
            i += seq_len
        else:
            i += 1

    return found


# 常见键盘模式硬编码（高频出现的直接匹配）
_COMMON_PATTERNS = [
    "qwerty", "qwert", "qwer", "asdf", "asdfgh", "zxcv", "zxcvbn",
    "1qaz", "2wsx", "3edc", "4rfv", "1q2w3e", "1qaz2wsx",
    "qazwsx", "qazwsxedc",
    "!@#$%", "!@#$", "!@#$%^", "!@#$%^&*",
]


def _find_common_patterns(password: str) -> list[dict]:
    """直接匹配高频键盘模式。"""
    pw_lower = password.lower()
    found: list[dict] = []

    for pat in _COMMON_PATTERNS:
        idx = pw_lower.find(pat)
        if idx != -1:
            found.append({
                "pattern": password[idx : idx + len(pat)],
                "position": idx,
                "length": len(pat),
                "direction": "common",
            })

    return found


def check_keyboard_patterns(password: str) -> dict:
    """执行完整的键盘模式检测。"""
    all_patterns: list[dict] = []

    # 1) 行内连续序列
    all_patterns.extend(_find_sequences(password, _ROWS, _MIN_SEQ_LEN))
    all_patterns.extend(_find_sequences(password, _NUMPAD, _MIN_SEQ_LEN))

    # 2) 高频模式直接匹配
    all_patterns.extend(_find_common_patterns(password))

    # 3) 相邻键模式
    all_patterns.extend(_find_adjacent_patterns(password))

    # 去重（按 position + pattern 去重）
    seen = set()
    unique: list[dict] = []
    for p in all_patterns:
        key = (p["position"], p["pattern"].lower())
        if key not in seen:
            seen.add(key)
            unique.append(p)

    unique.sort(key=lambda x: x["position"])

    # 计算覆盖率
    covered = set()
    for p in unique:
        for j in range(p["position"], p["position"] + p["length"]):
            covered.add(j)
    coverage = len(covered) / len(password) if password else 0

    return {
        "has_pattern": len(unique) > 0,
        "patterns": unique,
        "pattern_count": len(unique),
        "coverage": round(coverage, 2),
        "risk_level": (
            "high" if coverage > 0.5
            else "medium" if coverage > 0.2
            else "low"
        ),
    }


@register_tool("keyboard_pattern_check")
async def keyboard_pattern_check_tool(state: PassAgentState) -> dict:
    """检测口令中的键盘连续模式（如 qwerty, asdf, 1qaz2wsx）。"""
    params = state.get("action_params", {})
    password = params.get("password", "")

    result = check_keyboard_patterns(password)

    return {"_tool_result": result}
