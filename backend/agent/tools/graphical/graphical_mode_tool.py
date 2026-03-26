"""graphical_mode 工具：打开 PassInfinity 独立体验页

设计说明
--------
图形口令体验被收敛到独立页面 /lab/passinfinity：
1. Agent 调用 graphical_mode
2. 后端通过 SSE 推送 passinfinity_open 事件
3. 前端切换到体验页，并带上 mode 查询参数
"""
from __future__ import annotations

from agent.graph import register_tool
from agent.state import PassAgentState

_MODE_INFO = {
    "select": {
        "title": "PassInfinity 因子选择",
        "description": "进入 PassInfinity 后，你可以先选择要体验的因子类型，再进入对应的独立界面。",
        "instructions": [
            "先从图片记忆点、地图位置或富文本标记里选一个入口",
            "每种因子都是单独界面，不会混在同一屏",
            "如果需要，可以在页面内再切换到其他因子继续组合",
            "保存后可以回到对话里让我帮你解释结果",
        ],
    },
    "image": {
        "title": "PassInfinity 图片因子体验",
        "description": "进入体验页后，你可以选择图片并依次点击若干个位置，生成带图片因子的多因子方案。",
        "instructions": [
            "先在体验页里选择一张图片",
            "在图片上依次点击几个记忆点",
            "需要的话，再补充文本或地图位置因子",
            "保存后可以回到对话里让我帮你解释结果",
        ],
    },
    "map": {
        "title": "PassInfinity 地图因子体验",
        "description": "进入体验页后，你可以在地图上标记若干个位置，生成带位置因子的多因子方案。",
        "instructions": [
            "先在地图上找到你熟悉的区域",
            "依次点击几个有意义的位置",
            "需要的话，再补充文本或图片因子",
            "保存后可以回到对话里让我帮你解释结果",
        ],
    },
    "richtext": {
        "title": "PassInfinity 富文本标记体验",
        "description": "进入体验页后，你可以通过文本内容和强调样式，生成带文字标记因子的多因子方案。",
        "instructions": [
            "先写下你想作为标记的文字内容",
            "再选择只对你自己有意义的强调样式",
            "如果需要，可以继续切换到图片或地图因子",
            "保存后可以回到对话里让我帮你解释结果",
        ],
    },
}


@register_tool("graphical_mode")
async def graphical_mode_tool(state: PassAgentState) -> dict:
    """打开独立体验页（图片或地图模式）。"""
    params = state.get("action_params", {})
    mode = params.get("mode", "select")

    if mode not in _MODE_INFO:
        return {
            "_tool_result": {
                "error": f"不支持的图形口令模式: {mode}，可选 select / image / map / richtext"
            },
        }

    info = _MODE_INFO[mode]

    path = "/lab/passinfinity" if mode == "select" else f"/lab/passinfinity/{mode}"

    event_queue = state.get("_event_queue")
    if event_queue is not None:
        await event_queue.put({
            "event": "passinfinity_open",
            "data": {
                "path": path,
                "mode": mode,
                "title": info["title"],
                "description": info["description"],
                "instructions": info["instructions"],
            },
        })

    return {
        "_tool_result": {
            "status": "waiting_for_user",
            "path": path,
            "mode": mode,
            "title": info["title"],
            "description": info["description"],
            "instructions": info["instructions"],
        },
    }
