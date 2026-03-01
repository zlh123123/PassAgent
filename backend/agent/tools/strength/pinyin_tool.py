"""pinyin_check 工具：检测口令中的拼音组合"""
from __future__ import annotations

import json
import os
import re
from functools import lru_cache

from agent.graph import register_tool
from agent.state import PassAgentState

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")


# 完整的汉语拼音音节表（不含声调）
_FALLBACK_SYLLABLES = [
    "a", "ai", "an", "ang", "ao",
    "ba", "bai", "ban", "bang", "bao", "bei", "ben", "beng", "bi", "bian", "biao", "bie", "bin", "bing", "bo", "bu",
    "ca", "cai", "can", "cang", "cao", "ce", "cen", "ceng", "cha", "chai", "chan", "chang", "chao", "che", "chen", "cheng", "chi", "chong", "chou", "chu", "chua", "chuai", "chuan", "chuang", "chui", "chun", "chuo", "ci", "cong", "cou", "cu", "cuan", "cui", "cun", "cuo",
    "da", "dai", "dan", "dang", "dao", "de", "dei", "den", "deng", "di", "dia", "dian", "diao", "die", "ding", "diu", "dong", "dou", "du", "duan", "dui", "dun", "duo",
    "e", "ei", "en", "eng", "er",
    "fa", "fan", "fang", "fei", "fen", "feng", "fo", "fou", "fu",
    "ga", "gai", "gan", "gang", "gao", "ge", "gei", "gen", "geng", "gong", "gou", "gu", "gua", "guai", "guan", "guang", "gui", "gun", "guo",
    "ha", "hai", "han", "hang", "hao", "he", "hei", "hen", "heng", "hong", "hou", "hu", "hua", "huai", "huan", "huang", "hui", "hun", "huo",
    "ji", "jia", "jian", "jiang", "jiao", "jie", "jin", "jing", "jiong", "jiu", "ju", "juan", "jue", "jun",
    "ka", "kai", "kan", "kang", "kao", "ke", "ken", "keng", "kong", "kou", "ku", "kua", "kuai", "kuan", "kuang", "kui", "kun", "kuo",
    "la", "lai", "lan", "lang", "lao", "le", "lei", "leng", "li", "lia", "lian", "liang", "liao", "lie", "lin", "ling", "liu", "lo", "long", "lou", "lu", "luan", "lun", "luo", "lv", "lve",
    "ma", "mai", "man", "mang", "mao", "me", "mei", "men", "meng", "mi", "mian", "miao", "mie", "min", "ming", "miu", "mo", "mou", "mu",
    "na", "nai", "nan", "nang", "nao", "ne", "nei", "nen", "neng", "ni", "nian", "niang", "niao", "nie", "nin", "ning", "niu", "nong", "nou", "nu", "nuan", "nun", "nuo", "nv", "nve",
    "o", "ou",
    "pa", "pai", "pan", "pang", "pao", "pei", "pen", "peng", "pi", "pian", "piao", "pie", "pin", "ping", "po", "pou", "pu",
    "qi", "qia", "qian", "qiang", "qiao", "qie", "qin", "qing", "qiong", "qiu", "qu", "quan", "que", "qun",
    "ran", "rang", "rao", "re", "ren", "reng", "ri", "rong", "rou", "ru", "rua", "ruan", "rui", "run", "ruo",
    "sa", "sai", "san", "sang", "sao", "se", "sen", "seng", "sha", "shai", "shan", "shang", "shao", "she", "shei", "shen", "sheng", "shi", "shou", "shu", "shua", "shuai", "shuan", "shuang", "shui", "shun", "shuo", "si", "song", "sou", "su", "suan", "sui", "sun", "suo",
    "ta", "tai", "tan", "tang", "tao", "te", "teng", "ti", "tian", "tiao", "tie", "ting", "tong", "tou", "tu", "tuan", "tui", "tun", "tuo",
    "wa", "wai", "wan", "wang", "wei", "wen", "weng", "wo", "wu",
    "xi", "xia", "xian", "xiang", "xiao", "xie", "xin", "xing", "xiong", "xiu", "xu", "xuan", "xue", "xun",
    "ya", "yan", "yang", "yao", "ye", "yi", "yin", "ying", "yo", "yong", "you", "yu", "yuan", "yue", "yun",
    "za", "zai", "zan", "zang", "zao", "ze", "zei", "zen", "zeng", "zha", "zhai", "zhan", "zhang", "zhao", "zhe", "zhei", "zhen", "zheng", "zhi", "zhong", "zhou", "zhu", "zhua", "zhuai", "zhuan", "zhuang", "zhui", "zhun", "zhuo", "zi", "zong", "zou", "zu", "zuan", "zui", "zun", "zuo",
]

# 单字母音节，匹配时跳过以避免误报
_SINGLE_CHAR_SYLLABLES = {"a", "e", "o"}

# 连续拼音最小总长度
_MIN_PINYIN_SPAN = 4


@lru_cache(maxsize=1)
def _load_pinyin_set() -> set[str]:
    """加载拼音音节表。"""
    path = os.path.join(_DATA_DIR, "pinyin_dict.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        syllables = data.get("syllables", [])
        if syllables:
            return set(s.lower() for s in syllables)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return set(_FALLBACK_SYLLABLES)


def _greedy_pinyin_match(text: str, syllables: set[str]) -> list[dict]:
    """贪心匹配：从左到右尽可能匹配最长的拼音音节。"""
    result: list[dict] = []
    i = 0
    while i < len(text):
        matched = False
        for end in range(min(i + 6, len(text)), i, -1):
            candidate = text[i:end]
            if candidate in syllables and candidate not in _SINGLE_CHAR_SYLLABLES:
                result.append({"syllable": candidate, "position": i})
                i = end
                matched = True
                break
        if not matched:
            i += 1
    return result


def check_pinyin(password: str) -> dict:
    """检测口令中的拼音组合。"""
    if not password:
        return {"has_pinyin": False, "pinyin_segments": [], "risk_level": "low"}

    syllables = _load_pinyin_set()
    pw_lower = password.lower()

    # 提取纯字母段
    alpha_spans = [(m.start(), m.group()) for m in re.finditer(r"[a-zA-Z]+", pw_lower)]

    all_segments: list[dict] = []
    for span_start, span_text in alpha_spans:
        matches = _greedy_pinyin_match(span_text, syllables)
        if not matches:
            continue

        # 拼音覆盖的字符总长度
        covered = sum(len(m["syllable"]) for m in matches)
        if covered < _MIN_PINYIN_SPAN:
            continue

        pinyin_coverage = round(covered / len(span_text), 2)

        # 调整 position 为原始密码中的位置
        adjusted_syllables = [m["syllable"] for m in matches]

        all_segments.append({
            "span": password[span_start: span_start + len(span_text)],
            "syllables": adjusted_syllables,
            "pinyin_coverage": pinyin_coverage,
            "position": span_start,
        })

    # 只保留拼音覆盖率 >= 0.7 的段（避免英文单词误报）
    significant = [s for s in all_segments if s["pinyin_coverage"] >= 0.7]

    has_pinyin = len(significant) > 0
    risk = (       "high" if any(s["pinyin_coverage"] >= 0.9 for s in significant)
        else "medium" if has_pinyin
        else "low"
    )

    return {
        "has_pinyin": has_pinyin,
        "pinyin_segments": significant,
        "risk_level": risk,
    }


@register_tool("pinyin_check")
async def pinyin_check_tool(state: PassAgentState) -> dict:
    """检测口令中的拼音组合。"""
    params = state.get("action_params", {})
    password = params.get("password", "")
    return {"_tool_result": check_pinyin(password)}
