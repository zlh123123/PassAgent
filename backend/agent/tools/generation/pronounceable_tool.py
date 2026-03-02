"""pronounceable_generate 工具：生成可发音的随机口令

使用辅音-元音交替（CV 音节）+ 随机数字/符号插入的方式，
生成看似随机但可读可念的口令。
"""
from __future__ import annotations

import math
import secrets

from agent.graph import register_tool
from agent.state import PassAgentState

# 辅音和元音音素组合
_CONSONANTS = [
    "b", "c", "d", "f", "g", "h", "j", "k", "l", "m",
    "n", "p", "r", "s", "t", "v", "w", "z",
    "bl", "br", "ch", "cl", "cr", "dr", "fl", "fr", "gl", "gr",
    "pl", "pr", "sh", "sk", "sl", "sm", "sn", "sp", "st", "str",
    "sw", "th", "tr", "tw", "wh", "wr",
]

_VOWELS = [
    "a", "e", "i", "o", "u",
    "ai", "au", "ea", "ee", "oo", "ou",
    "ar", "er", "ir", "or", "ur",
]

_FINAL_CONSONANTS = [
    "b", "ck", "d", "g", "k", "l", "m", "n", "ng",
    "p", "r", "s", "sh", "t", "th", "x", "z",
]

_SPECIALS = "!@#$%&*_+-="


def _generate_syllable() -> str:
    """生成一个 CVC 或 CV 音节。"""
    syl = secrets.choice(_CONSONANTS) + secrets.choice(_VOWELS)
    # 50% 概率追加尾辅音
    if secrets.randbelow(2):
        syl += secrets.choice(_FINAL_CONSONANTS)
    return syl


def generate_pronounceable(length: int = 12, add_digit: bool = True, add_special: bool = True) -> dict:
    """生成一个可发音的随机口令。"""
    syllables: list[str] = []
    current_len = 0

    while current_len < length:
        syl = _generate_syllable()
        syllables.append(syl)
        current_len += len(syl)

    # 拼接并截断到目标长度
    raw = "".join(syllables)[:length]

    # 随机大写 1-2 个位置
    pw_list = list(raw)
    upper_count = min(2, len(pw_list))
    positions = set()
    while len(positions) < upper_count:
        pos = secrets.randbelow(len(pw_list))
        if pw_list[pos].isalpha():
            positions.add(pos)
    for pos in positions:
        pw_list[pos] = pw_list[pos].upper()

    # 插入数字和特殊字符
    if add_digit:
        insert_pos = secrets.randbelow(len(pw_list))
        pw_list.insert(insert_pos, str(secrets.randbelow(10)))
    if add_special:
        insert_pos = secrets.randbelow(len(pw_list))
        pw_list.insert(insert_pos, secrets.choice(_SPECIALS))

    password = "".join(pw_list)

    return {
        "password": password,
        "syllables": [s for s in syllables],
        "length": len(password),
        "pronounceable_core": raw,
    }


@register_tool("pronounceable_generate")
async def pronounceable_generate_tool(state: PassAgentState) -> dict:
    """生成可发音的随机口令。"""
    params = state.get("action_params", {})
    length = params.get("length", 12)

    # 生成多个候选
    candidates = [generate_pronounceable(length=length) for _ in range(5)]

    return {
        "_tool_result": {
            "candidates": candidates,
            "count": len(candidates),
        }
    }
