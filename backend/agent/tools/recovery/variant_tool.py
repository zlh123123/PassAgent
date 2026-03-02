"""variant_expand 工具：对候选口令进行常见变体扩展

参考 hashcat rule-based attack 常见函数的 Python 实现子集：
- 大小写变换（capitalize, toggleCase, upper, lower）
- Leet speak 替换
- 追加/前置数字和符号
- 反转
- 重复
- 首尾截断/追加

参考: https://hashcat.net/wiki/doku.php?id=rule_based_attack
"""
from __future__ import annotations

from agent.graph import register_tool
from agent.state import PassAgentState

# 常见 leet speak 映射
_LEET_MAP = {
    "a": ["@", "4"],
    "e": ["3"],
    "i": ["1", "!"],
    "o": ["0"],
    "s": ["$", "5"],
    "t": ["7"],
    "l": ["1"],
    "b": ["8"],
    "g": ["9"],
}

# 常见追加后缀
_COMMON_SUFFIXES = [
    "1", "12", "123", "1234", "!",  "!!", "@", "#",
    "01", "00", "99", "88", "66", "520", "666", "888",
    ".", "~", "!", "@#", "abc",
]

# 常见追加前缀
_COMMON_PREFIXES = ["1", "!", "@", "#", "the", "my", "i"]


def _apply_rules(password: str) -> list[str]:
    """对单个口令应用 hashcat 风格的变换规则。"""
    variants: set[str] = set()
    pw = password

    # --- 大小写变换 ---
    variants.add(pw.capitalize())         # 首字母大写
    variants.add(pw.upper())              # 全大写
    variants.add(pw.lower())              # 全小写
    variants.add(pw.swapcase())           # 大小写反转
    # Toggle 第一个字符
    if pw:
        toggled = pw[0].swapcase() + pw[1:]
        variants.add(toggled)

    # --- Leet speak ---
    leet = list(pw.lower())
    for i, c in enumerate(leet):
        if c in _LEET_MAP:
            leet[i] = _LEET_MAP[c][0]  # 只取第一个替换
    leet_str = "".join(leet)
    if leet_str != pw.lower():
        variants.add(leet_str)
        variants.add(leet_str.capitalize())

    # 部分 leet（只替换元音）
    partial_leet = list(pw.lower())
    for i, c in enumerate(partial_leet):
        if c in ("a", "e", "i", "o"):
            partial_leet[i] = _LEET_MAP[c][0]
    partial_str = "".join(partial_leet)
    if partial_str != pw.lower() and partial_str != leet_str:
        variants.add(partial_str)

    # --- 追加后缀 ---
    for suffix in _COMMON_SUFFIXES:
        variants.add(pw + suffix)
        variants.add(pw.capitalize() + suffix)

    # --- 追加前缀 ---
    for prefix in _COMMON_PREFIXES:
        variants.add(prefix + pw)

    # --- 反转 ---
    variants.add(pw[::-1])

    # --- 重复 ---
    variants.add(pw + pw)          # duplicate
    if len(pw) >= 4:
        variants.add(pw[:len(pw)//2] * 2)  # 前半部分重复

    # --- 截断/追加 ---
    if len(pw) > 1:
        variants.add(pw[1:])       # 删首字符
        variants.add(pw[:-1])      # 删尾字符

    # --- 删除所有数字/只保留数字 ---
    alpha_only = "".join(c for c in pw if c.isalpha())
    digit_only = "".join(c for c in pw if c.isdigit())
    if alpha_only and alpha_only != pw:
        variants.add(alpha_only)
    if digit_only and digit_only != pw:
        variants.add(digit_only)

    # 移除原始密码本身
    variants.discard(pw)

    return sorted(variants)


def expand_variants(base_list: list[str], max_per_base: int = 50, max_total: int = 500) -> dict:
    """对候选列表中每个口令进行变体扩展。"""
    all_variants: list[dict] = []
    seen: set[str] = set()

    for base in base_list:
        if not base:
            continue
        variants = _apply_rules(base)[:max_per_base]
        for v in variants:
            if v not in seen:
                seen.add(v)
                all_variants.append({"base": base, "variant": v})
                if len(all_variants) >= max_total:
                    break
        if len(all_variants) >= max_total:
            break

    return {
        "variants": all_variants,
        "count": len(all_variants),
        "base_count": len(base_list),
    }


@register_tool("common_variant_expand")
async def variant_expand_tool(state: PassAgentState) -> dict:
    """对候选口令进行常见变体扩展（hashcat 规则子集）。"""
    params = state.get("action_params", {})
    base_list = params.get("base_list", [])

    result = expand_variants(base_list)
    return {"_tool_result": result}
