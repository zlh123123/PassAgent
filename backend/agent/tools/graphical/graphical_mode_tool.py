"""graphical_mode 工具：唤起前端图形口令组件并处理结果

设计说明
--------
图形口令是前后端协作流程：
1. Agent 决策调用 graphical_mode → 向前端推送 graphical_start 事件
   （携带 mode、使用说明等）
2. 前端展示组件，用户操作完成后将选点数据回传后端
3. 后端量化选点熵值，写入 tool_history 供后续 respond 使用

该工具本身只负责第 1 步：推送启动事件 + 返回一条引导消息，
前端回传数据后由 /api/chat/graphical_result 端点写入 session state。
"""
from __future__ import annotations

from agent.graph import register_tool
from agent.state import PassAgentState

# 图形口令模式的说明文本，会推送给前端用于展示
_MODE_INFO = {
    "image": {
        "title": "图片选点口令",
        "description": "请在图片上依次点击若干个位置作为你的口令。系统会记录你的选点坐标序列。",
        "min_points": 4,
        "max_points": 10,
        "instructions": [
            "选择一张你熟悉的图片（或使用系统默认图片）",
            "在图片上依次点击 4-10 个点",
            "记住点击的顺序和大致位置",
            "验证时需要按相同顺序点击相近位置",
        ],
    },
    "map": {
        "title": "地图选点口令",
        "description": "请在地图上依次标记若干个地点作为你的口令。系统会记录你选择的地理坐标序列。",
        "min_points": 3,
        "max_points": 8,
        "instructions": [
            "在地图上搜索或缩放到你熟悉的区域",
            "依次点击 3-8 个有意义的地点",
            "记住选择的地点和顺序",
            "验证时需要按相同顺序选择相近地点",
        ],
    },
}


@register_tool("graphical_mode")
async def graphical_mode_tool(state: PassAgentState) -> dict:
    """唤起前端图形口令组件（图片选点或地图选点）。

    向前端推送 graphical_start SSE 事件，前端据此渲染对应组件。
    用户完成选点后，前端将数据回传至后端，后续由 Agent 解读结果。
    """
    params = state.get("action_params", {})
    mode = params.get("mode", "image")

    if mode not in _MODE_INFO:
        return {
            "_tool_result": {"error": f"不支持的图形口令模式: {mode}，可选 image / map"},
        }

    info = _MODE_INFO[mode]

    # 通过 event_queue 推送启动事件给前端
    event_queue = state.get("_event_queue")
    if event_queue is not None:
        await event_queue.put({
            "event": "graphical_start",
            "data": {
                "mode": mode,
                "title": info["title"],
                "description": info["description"],
                "min_points": info["min_points"],
                "max_points": info["max_points"],
                "instructions": info["instructions"],
            },
        })

    return {
        "_tool_result": {
            "status": "waiting_for_user",
            "mode": mode,
            "title": info["title"],
            "description": info["description"],
            "instructions": info["instructions"],
        },
    }
