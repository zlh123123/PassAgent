"""Respond 节点：汇总工具结果，生成最终用户回复（流式）"""
from __future__ import annotations

import json
from openai import AsyncOpenAI

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from agent.state import PassAgentState


def _build_respond_system_prompt(state: PassAgentState) -> str:
    """根据 tool_history 长度选择回复模式，构建 system prompt。"""
    tool_count = len(state.get("tool_history", []))

    if tool_count == 0:
        mode_hint = "这是一个闲聊或拒绝场景，无工具调用结果。如果是与口令安全无关的问题，友好地引导用户使用口令相关功能。如果是恶意请求，礼貌拒绝。如果是信息不足，追问用户。"
    elif tool_count <= 2:
        mode_hint = "工具调用结果较少，请给出简短精炼的回复。"
    else:
        mode_hint = "工具调用结果较多，请给出详细的分析报告。"

    return f"""\
你是 PassAgent，一个基于大语言模型的口令安全智能助手。请根据工具调用结果生成最终回复。

## 回复要求
- 用中文回复，保持专业且友好的语气
- {mode_hint}
- 在回复末尾自然地附带 2-3 个引导性建议（作为回复文本的一部分，不要单独结构化输出）
- 引导建议用换行和 emoji 前缀，例如：
  - 🔍 查看这个密码是否泄露
  - 🔑 帮我生成一个更安全的密码
- 不要暴露内部工具名称，用自然语言描述分析过程
- 如果涉及密码强度评分，用直观的方式表达（如 "评分 1/4，较弱"）"""


def _build_tool_results_message(state: PassAgentState) -> str:
    """将 tool_history 格式化为 LLM 可读的上下文。"""
    if not state.get("tool_history"):
        return ""

    parts = ["以下是本轮工具调用结果：\n"]
    for i, t in enumerate(state["tool_history"], 1):
        tool_name = t["tool_name"]
        params = json.dumps(t.get("params", {}), ensure_ascii=False)
        result = json.dumps(t.get("result", {}), ensure_ascii=False)
        parts.append(f"{i}. [{tool_name}] 参数: {params}\n   结果: {result}\n")

    # 记忆上下文
    if state.get("memories"):
        parts.append("\n用户记忆：")
        for mem in state["memories"]:
            parts.append(f"  - [{mem.get('memory_type', '')}] {mem.get('content', '')}")

    return "\n".join(parts)


async def respond_node(state: PassAgentState) -> dict:
    """Respond 节点：流式生成最终回复。

    通过 state 中注入的 event_queue 将 response_chunk 事件推送给 SSE。
    返回对 state 的 partial update，将完整回复追加到 messages。
    """
    client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    event_queue = state.get("_event_queue")  # 运行时注入，不属于 TypedDict

    # 构建消息
    messages = [{"role": "system", "content": _build_respond_system_prompt(state)}]

    # 对话历史
    for msg in state["messages"]:
        if hasattr(msg, "type"):
            role = "user" if msg.type == "human" else "assistant"
        else:
            role = msg.get("role", "user")
        content = msg.content if hasattr(msg, "content") else msg.get("content", "")
        messages.append({"role": role, "content": content})

    # 工具结果上下文
    tool_context = _build_tool_results_message(state)
    if tool_context:
        messages.append({"role": "system", "content": tool_context})

    # 流式调用 LLM
    stream = await client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        stream=True,
    )

    full_content = ""
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_content += content
            # 推送 SSE 事件
            if event_queue is not None:
                await event_queue.put({
                    "event": "response_chunk",
                    "data": {"content": content},
                })

    # 将完整回复作为 AIMessage 追加到 messages
    from langchain_core.messages import AIMessage
    return {
        "messages": [AIMessage(content=full_content)],
        "next_action": None,
    }
