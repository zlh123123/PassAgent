"""pcfg_analyze 工具：分析口令的 PCFG 结构模式"""
from __future__ import annotations

from agent.graph import register_tool
from agent.state import PassAgentState

# 高频 PCFG 结构（来自公开泄露数据集统计）
_COMMON_STRUCTURES = {
    "L6",       # 纯6位小写
    "L7",
    "L8",
    "D6",       # 纯6位数字
    "D8",
    "D10",
    "L6D2",     # 小写+数字
    "L5D3",
    "L4D4",
    "L8D2",
    "L6D4",
    "L3D4",
    "L4D3",
    "L5D4",
    "L7D3",
    "L8D4",
    "U1L5D2",   # 首字母大写+小写+数字
    "U1L7",
    "U1L5D4",
    "U1L7D2",
    "U1L6D2",
    "U1L4D4",
    "D4L4",     # 数字+小写
    "D2L6",
    "D4L6",
    "L6S1",     # 小写+特殊符号
    "L8S1",
    "L6D2S1",
    "L4D4S1",
    "U1L5D2S1",
    "D6S1",
    "L4S1D4",
    "D8L2",
    "D4S1D4",
}


def _classify_char(c: str) -> str:
    """将字符分类为 U(大写) L(小写) D(数字) S(特殊)。"""
    if c.isupper():
        return "U"
    elif c.islower():
        return "L"
    elif c.isdigit():
        return "D"
    else:
        return "S"


def parse_pcfg_structure(password: str) -> list[dict]:
    """将口令解析为 PCFG 段列表。"""
    if not password:
        return []

    segments: list[dict] = []
    current_type = _classify_char(password[0])
    current_start = 0

    for i in range(1, len(password)):
        char_type = _classify_char(password[i])
        if char_type != current_type:
            segments.append({
                "type": current_type,
                "value": password[current_start:i],
                "length": i - current_start,
            })
            current_type = char_type
            current_start = i

    segments.append({
        "type": current_type,
        "value": password[current_start:],
        "length": len(password) - current_start,
    })

    return segments


def analyze_pcfg(password: str) -> dict:
    """分析口令的 PCFG 结构。"""
    if not password:
        return {
            "structure": "",
            "segments": [],
            "is_common_structure": False,
            "segment_count": 0,
            "risk_level": "low",
        }

    segments = parse_pcfg_structure(password)

    # 生成结构字符串，如 "U1L5D2S1"
    structure = "".join(f"{seg['type']}{seg['length']}" for seg in segments)

    is_common = structure in _COMMON_STRUCTURES

    # 段数越少结构越简单，风险越高
    seg_count = len(segments)
    if is_common:
        risk = "high"
    elif seg_count <= 2:
        risk = "medium"
    else:
        risk = "low"

    return {
        "structure": structure,
        "segments": segments,
        "is_common_structure": is_common,
        "segment_count": seg_count,
        "risk_level": risk,
    }


@register_tool("pcfg_analyze")
async def pcfg_analyze_tool(state: PassAgentState) -> dict:
    """分析口令的 PCFG 结构模式，判断是否为常见结构。"""
    params = state.get("action_params", {})
    password = params.get("password", "")
    return {"_tool_result": analyze_pcfg(password)}
