"""PassAgentState: Agent 运行时状态定义"""
from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langgraph.graph import MessagesState


class ToolResult(TypedDict, total=False):
    """单次工具调用记录"""
    tool_name: str
    params: dict
    result: dict


class PassAgentState(MessagesState):
    """LangGraph 状态，继承 MessagesState 自动管理 messages 列表。

    Attributes:
        user_id: 当前用户 ID
        session_id: 当前会话 ID
        memories: 本轮检索到的用户记忆
        tool_history: 本轮已调用的工具及结果（append-only）
        next_action: planner 决定的下一步动作（工具名 / "respond" / None）
        action_params: 传给工具的参数
        uploaded_files: 本轮上传的文件信息
        loop_count: 当前循环次数，用于防止死循环
        event_queue: 运行时注入的 asyncio.Queue，用于向 SSE 推送事件
    """
    user_id: str
    session_id: str
    memories: list[dict]
    tool_history: Annotated[list[ToolResult], operator.add]
    next_action: str | None
    action_params: dict
    uploaded_files: list[dict]
    loop_count: int
