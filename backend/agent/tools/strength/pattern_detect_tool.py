"""pattern_detect 工具：键盘模式 + 拼音组合 + 日期模式（合并 keyboard + pinyin + date）"""
from __future__ import annotations

import json
import os
import re
from functools import lru_cache

from agent.graph import register_tool
from agent.state import PassAgentState

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")


# ================================================================
#  键盘模式检测
# ================================================================

_ROWS = [
    "1234567890",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
]

_NUMPAD = [
    "789",
    "456",
    "123",
    "0",
]

_MIN_SEQ_LEN = 3

_COMMON_KB_PATTERNS = [
    "qwerty", "qwert", "qwer", "asdf", "asdfgh", "zxcv", "zxcvbn",
    "1qaz", "2wsx", "3edc", "4rfv", "1q2w3e", "1qaz2wsx",
    "qazwsx", "qazwsxedc",
    "!@#$%", "!@#$", "!@#$%^", "!@#$%^&*",
]


def _find_sequences(password: str, layout: list[str], min_len: int) -> list[dict]:
    pw_lower = password.lower()
    found: list[dict] = []
    for row in layout:
        if len(row) < min_len:
            continue
        for seq_source, direction in [(row, "forward"), (row[::-1], "reverse")]:
            i = 0
            while i < len(pw_lower):
                j = seq_source.find(pw_lower[i])
                if j == -1:
                    i += 1
                    continue
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
                        "type": "keyboard_sequence",
                        "detail": direction,
                    })
                    i += match_len
                else:
                    i += 1
    return found


def _find_adjacent_patterns(password: str) -> list[dict]:
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
            if row_diff <= 1 and col_diff <= 1 and (row_diff + col_diff) > 0:
                seq_len += 1
            else:
                break
        if seq_len >= _MIN_SEQ_LEN:
            found.append({
                "pattern": password[i : i + seq_len],
                "position": i,
                "length": seq_len,
                "type": "keyboard_adjacent",
                "detail": "adjacent",
            })
            i += seq_len
        else:
            i += 1
    return found


def _find_common_kb(password: str) -> list[dict]:
    pw_lower = password.lower()
    found: list[dict] = []
    for pat in _COMMON_KB_PATTERNS:
        idx = pw_lower.find(pat)
        if idx != -1:
            found.append({
                "pattern": password[idx : idx + len(pat)],
                "position": idx,
                "length": len(pat),
                "type": "keyboard_common",
                "detail": pat,
            })
    return found


def _detect_keyboard(password: str) -> list[dict]:
    all_p: list[dict] = []
    all_p.extend(_find_sequences(password, _ROWS, _MIN_SEQ_LEN))
    all_p.extend(_find_sequences(password, _NUMPAD, _MIN_SEQ_LEN))
    all_p.extend(_find_common_kb(password))
    all_p.extend(_find_adjacent_patterns(password))
    # 去重
    seen = set()
    unique: list[dict] = []
    for p in all_p:
        key = (p["position"], p["pattern"].lower())
        if key not in seen:
            seen.add(key)
            unique.append(p)
    unique.sort(key=lambda x: x["position"])
    return unique


# ================================================================
#  拼音检测
# ================================================================

_SINGLE_CHAR_SYLLABLES = {"a", "e", "o"}
_MIN_PINYIN_SPAN = 4

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


@lru_cache(maxsize=1)
def _load_pinyin_set() -> set[str]:
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


def _detect_pinyin(password: str) -> list[dict]:
    if not password:
        return []
    syllables = _load_pinyin_set()
    pw_lower = password.lower()
    alpha_spans = [(m.start(), m.group()) for m in re.finditer(r"[a-zA-Z]+", pw_lower)]

    results: list[dict] = []
    for span_start, span_text in alpha_spans:
        matches = _greedy_pinyin_match(span_text, syllables)
        if not matches:
            continue
        covered = sum(len(m["syllable"]) for m in matches)
        if covered < _MIN_PINYIN_SPAN:
            continue
        pinyin_coverage = round(covered / len(span_text), 2)
        if pinyin_coverage < 0.7:
            continue
        results.append({
            "pattern": password[span_start: span_start + len(span_text)],
            "position": span_start,
            "length": len(span_text),
            "type": "pinyin",
            "detail": ", ".join(m["syllable"] for m in matches),
            "pinyin_coverage": pinyin_coverage,
        })
    return results


# ================================================================
#  日期模式检测
# ================================================================

_DATE_PATTERNS: list[tuple[str, str]] = [
    (r"((?:19|20)\d{2})[-/.]?(0[1-9]|1[0-2])[-/.]?(0[1-9]|[12]\d|3[01])", "YYYY-MM-DD"),
    (r"(0[1-9]|[12]\d|3[01])[-/.]?(0[1-9]|1[0-2])[-/.]?((?:19|20)\d{2})", "DD-MM-YYYY"),
    (r"(0[1-9]|1[0-2])[-/.]?(0[1-9]|[12]\d|3[01])[-/.]?((?:19|20)\d{2})", "MM-DD-YYYY"),
    (r"(\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])", "YYMMDD"),
    (r"((?:19|20)\d{2})", "YYYY"),
    (r"(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])", "MMDD"),
]


def _validate_date(year: int, month: int, day: int) -> bool:
    if month < 1 or month > 12 or day < 1:
        return False
    days_in_month = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return day <= days_in_month[month]


def _detect_dates(password: str) -> list[dict]:
    if not password:
        return []
    found: list[dict] = []
    used_spans: list[tuple[int, int]] = []

    for pattern_re, fmt in _DATE_PATTERNS:
        for m in re.finditer(pattern_re, password):
            start, end = m.start(), m.end()
            if any(s <= start and end <= e for s, e in used_spans):
                continue

            groups = m.groups()
            valid = True
            if fmt == "YYYY-MM-DD" and len(groups) == 3:
                valid = _validate_date(int(groups[0]), int(groups[1]), int(groups[2]))
            elif fmt == "DD-MM-YYYY" and len(groups) == 3:
                valid = _validate_date(int(groups[2]), int(groups[1]), int(groups[0]))
            elif fmt == "MM-DD-YYYY" and len(groups) == 3:
                valid = _validate_date(int(groups[2]), int(groups[0]), int(groups[1]))
            if not valid:
                continue

            if fmt in ("YYYY", "MMDD") and len(password) > 12:
                continue

            found.append({
                "pattern": m.group(),
                "position": start,
                "length": end - start,
                "type": "date",
                "detail": fmt,
            })
            used_spans.append((start, end))

    # 保留最长匹配
    found.sort(key=lambda x: x["length"], reverse=True)
    final: list[dict] = []
    final_spans: list[tuple[int, int]] = []
    for item in found:
        s, e = item["position"], item["position"] + item["length"]
        if not any(fs <= s and e <= fe for fs, fe in final_spans):
            final.append(item)
            final_spans.append((s, e))
    return final


# ================================================================
#  统一入口
# ================================================================

def detect_all_patterns(password: str) -> dict:
    """执行全部模式检测并汇总。"""
    if not password:
        return {
            "patterns": [],
            "pattern_count": 0,
            "coverage": 0.0,
            "risk_level": "low",
            "summary": {"keyboard": 0, "pinyin": 0, "date": 0},
        }

    all_patterns: list[dict] = []
    all_patterns.extend(_detect_keyboard(password))
    all_patterns.extend(_detect_pinyin(password))
    all_patterns.extend(_detect_dates(password))
    all_patterns.sort(key=lambda x: x["position"])

    # 统计覆盖率
    covered = set()
    for p in all_patterns:
        for k in range(p["position"], p["position"] + p["length"]):
            covered.add(k)
    coverage = round(len(covered) / len(password), 2) if password else 0.0

    # 分类统计
    summary = {"keyboard": 0, "pinyin": 0, "date": 0}
    for p in all_patterns:
        t = p["type"]
        if t.startswith("keyboard"):
            summary["keyboard"] += 1
        elif t == "pinyin":
            summary["pinyin"] += 1
        elif t == "date":
            summary["date"] += 1

    risk = "high" if coverage > 0.5 else "medium" if coverage > 0.2 or all_patterns else "low"

    return {
        "patterns": all_patterns,
        "pattern_count": len(all_patterns),
        "coverage": coverage,
        "risk_level": risk,
        "summary": summary,
    }


@register_tool("pattern_detect")
async def pattern_detect_tool(state: PassAgentState) -> dict:
    """检测口令中的键盘模式、拼音组合和日期模式。"""
    params = state.get("action_params", {})
    password = params.get("password", "")
    return {"_tool_result": detect_all_patterns(password)}
