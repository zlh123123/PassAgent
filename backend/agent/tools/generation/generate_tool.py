"""generate_password 工具：基于种子词和约束条件生成安全口令

使用 Python secrets 模块保证密码学安全随机性。
支持两种模式：
1. 有种子词 → 将种子词进行安全变换（leet speak、插入随机字符、拼接）
2. 无种子词 → 纯随机生成符合约束的口令
"""
from __future__ import annotations

import math
import secrets
import string

from agent.graph import register_tool
from agent.state import PassAgentState

# Leet speak 映射（用于种子词变换）
_LEET_MAP = {
    "a": "@", "e": "3", "i": "!", "o": "0", "s": "$",
    "t": "7", "l": "1", "b": "8", "g": "9",
}

_SPECIAL_CHARS = "!@#$%^&*_+-="
_DIGITS = string.digits
_ALL_CHARS = string.ascii_letters + _DIGITS + _SPECIAL_CHARS


def _leet_transform(word: str) -> str:
    """随机 leet speak 变换：每个可替换字符有 50% 概率被替换。"""
    result = []
    for c in word:
        lower = c.lower()
        if lower in _LEET_MAP and secrets.randbelow(2):
            result.append(_LEET_MAP[lower])
        else:
            result.append(c)
    return "".join(result)


def _capitalize_random(word: str) -> str:
    """随机大写变换。"""
    result = []
    for c in word:
        if c.isalpha() and secrets.randbelow(3) == 0:
            result.append(c.upper())
        else:
            result.append(c)
    return "".join(result)


def _generate_from_seeds(seeds: list[str], constraints: dict) -> list[dict]:
    """基于种子词变换生成口令候选列表。"""
    min_len = constraints.get("min_length", 12)
    max_len = constraints.get("max_length", 32)
    require_upper = constraints.get("require_upper", True)
    require_digit = constraints.get("require_digit", True)
    require_special = constraints.get("require_special", True)
    preferred_specials = constraints.get("preferred_specials", _SPECIAL_CHARS)

    candidates: list[dict] = []

    # 策略1：种子词拼接 + leet speak
    for _ in range(3):
        parts = []
        for seed in seeds:
            variant = _leet_transform(seed) if secrets.randbelow(2) else _capitalize_random(seed)
            parts.append(variant)
        sep = secrets.choice(list(preferred_specials)) if preferred_specials else ""
        pw = sep.join(parts)
        # 补充长度
        while len(pw) < min_len:
            pw += secrets.choice(_DIGITS + preferred_specials)
        pw = pw[:max_len]
        candidates.append({"password": pw, "method": "seed_leet_join"})

    # 策略2：种子词首字母 + 随机填充
    initials = "".join(s[0].upper() for s in seeds if s)
    for _ in range(2):
        fill_len = max(min_len - len(initials) - 2, 4)
        fill = "".join(secrets.choice(string.ascii_lowercase + _DIGITS) for _ in range(fill_len))
        sep = secrets.choice(list(preferred_specials))
        pw = initials + sep + fill + secrets.choice(list(preferred_specials))
        candidates.append({"password": pw[:max_len], "method": "initials_fill"})

    # 策略3：单个种子词展开
    for seed in seeds[:2]:
        pw = _capitalize_random(seed)
        pw += secrets.choice(list(preferred_specials))
        pw += "".join(secrets.choice(_DIGITS) for _ in range(3))
        pw += secrets.choice(list(preferred_specials))
        pw += "".join(secrets.choice(string.ascii_lowercase) for _ in range(max(0, min_len - len(pw))))
        candidates.append({"password": pw[:max_len], "method": "seed_expand"})

    # 校验约束，不符合的做修补
    final: list[dict] = []
    for c in candidates:
        pw = c["password"]
        if require_upper and not any(ch.isupper() for ch in pw):
            pw = pw[0].upper() + pw[1:]
        if require_digit and not any(ch.isdigit() for ch in pw):
            pw = pw[:-1] + secrets.choice(_DIGITS)
        if require_special and not any(ch in string.punctuation for ch in pw):
            pw = pw + secrets.choice(list(preferred_specials))
        c["password"] = pw[:max_len]
        c["length"] = len(c["password"])
        final.append(c)

    return final


def _generate_random(constraints: dict) -> list[dict]:
    """纯随机生成口令。"""
    min_len = constraints.get("min_length", 16)
    max_len = constraints.get("max_length", 32)
    count = constraints.get("count", 5)
    preferred_specials = constraints.get("preferred_specials", _SPECIAL_CHARS)

    target_len = min(max(min_len, 16), max_len)
    charset = string.ascii_letters + _DIGITS + preferred_specials

    candidates: list[dict] = []
    for _ in range(count):
        # 保证包含所有必需类别
        parts = [
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.ascii_lowercase),
            secrets.choice(_DIGITS),
            secrets.choice(preferred_specials),
        ]
        remaining = target_len - len(parts)
        parts.extend(secrets.choice(charset) for _ in range(remaining))
        # 安全洗牌
        pw_list = list(parts)
        for i in range(len(pw_list) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            pw_list[i], pw_list[j] = pw_list[j], pw_list[i]
        pw = "".join(pw_list)
        # 计算信息熵
        entropy = round(target_len * math.log2(len(charset)), 1)
        candidates.append({
            "password": pw,
            "method": "random",
            "length": target_len,
            "entropy_bits": entropy,
        })

    return candidates


@register_tool("generate_password")
async def generate_password_tool(state: PassAgentState) -> dict:
    """基于种子词和约束条件生成口令候选。"""
    params = state.get("action_params", {})
    seeds = params.get("seeds", [])
    constraints = params.get("constraints", {})

    if seeds:
        candidates = _generate_from_seeds(seeds, constraints)
    else:
        candidates = _generate_random(constraints)

    return {
        "_tool_result": {
            "candidates": candidates,
            "count": len(candidates),
            "has_seeds": bool(seeds),
        }
    }
