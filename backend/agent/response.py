"""Respond 节点：汇总工具结果，生成最终用户回复（流式）"""
from __future__ import annotations

import json
import logging
from openai import AsyncOpenAI
from langchain_core.messages import AIMessage

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from agent.state import PassAgentState

logger = logging.getLogger(__name__)


def _build_respond_system_prompt(state: PassAgentState) -> str:
    """构建最终回复的 system prompt。"""
    tool_history = state.get("tool_history", [])
    tool_count = len(tool_history)

    base_persona = """
你叫 PassAgent，是用户的个人口令安全专家。你的核心职责是评估风险、发现隐患并提供加固建议。

你的回答必须：
1. 准确严谨：基于工具返回的数据说话，不要编造未检测到的风险。
2. 通俗易懂：将技术术语转化为用户能懂的语言。
3. 安全第一：如果工具返回了敏感信息（如明文密码），在回复中应进行打码处理（如 `P***d`），除非用户明确要求显示。
4. 简洁有条理：优先给结论，再给原因和建议。
""".strip()

    if tool_count == 0:
        task_instruction = """
当前状态：闲聊或意图识别阶段
- 如果用户是在打招呼，请热情回应并简述你能做什么（如：检测密码强度、生成安全口令、查询泄露信息、辅助恢复记忆片段）。
- 如果用户的问题超出了“口令安全”范畴，请礼貌地将话题引导回你的专业领域。
- 拒绝处理任何非法的破解请求（如“帮我破解隔壁的 WiFi”）。
""".strip()
    else:
        task_instruction = """
当前状态：分析报告生成阶段
请根据下方上下文中的工具结果生成回复，并遵循以下结构：

### 1. 核心结论
用一句话概括结果。

### 2. 详细分析
- 解读工具返回的数据，不要直接罗列 JSON 字段。
- 如果涉及评分，请用直观描述（如：🔴高危、🟡中等、🟢安全）。
- 解释为什么会得出这个结论。

### 3. 后续建议
- 给出 2-3 条具体、可执行的建议。
- 如果信息不足，也要明确告诉用户下一步该补充什么。
""".strip()

    return f"{base_persona}\n\n{task_instruction}"


def _build_tool_context(state: PassAgentState) -> str:
    """把工具结果和用户记忆整理成结构化文本，拼进唯一的 system message。"""
    context_parts: list[str] = []

    if state.get("tool_history"):
        tools_str = []
        for i, t in enumerate(state["tool_history"], 1):
            tool_name = t["tool_name"]
            result_str = json.dumps(t.get("result", {}), ensure_ascii=False)
            status = "成功" if t.get("status") != "error" else "失败"

            tools_str.append(
                f"""<tool_execution id="{i}">
<name>{tool_name}</name>
<status>{status}</status>
<result>{result_str}</result>
</tool_execution>"""
            )

        context_parts.append("<tool_outputs>\n" + "\n".join(tools_str) + "\n</tool_outputs>")

    if state.get("memories"):
        mem_str = []
        for mem in state["memories"]:
            m_type = mem.get("memory_type", "INFO")
            content = mem.get("content", "")
            mem_str.append(f"- [{m_type}] {content}")

        context_parts.append("<user_profile>\n" + "\n".join(mem_str) + "\n</user_profile>")

    if state.get("uploaded_files"):
        files_str = json.dumps(state["uploaded_files"], ensure_ascii=False)
        context_parts.append(f"<uploaded_files>\n{files_str}\n</uploaded_files>")

    return "\n\n".join(context_parts)


async def respond_node(state: PassAgentState) -> dict:
    """Respond 节点：流式生成最终回复。"""
    client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    event_queue = state.get("_event_queue")

    system_content = _build_respond_system_prompt(state)
    context_content = _build_tool_context(state)

    if context_content:
        system_content += f"\n\n请严格基于以下上下文回答用户，不要编造未出现的数据：\n{context_content}"

    messages = [{"role": "system", "content": system_content}]

    # 追加历史对话
    for msg in state["messages"]:
        if hasattr(msg, "type"):
            role = "user" if msg.type == "human" else "assistant"
        else:
            role = msg.get("role", "user")

        content = msg.content if hasattr(msg, "content") else str(msg.get("content", ""))
        messages.append({"role": role, "content": content})

    logger.info("Respond request: model=%s, message_count=%d", LLM_MODEL, len(messages))

    full_content = ""
    try:
        stream = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            stream=True,
            temperature=0.5,
            max_tokens=2048,
            extra_body={
                "repetition_penalty": 1.05,
                "chat_template_kwargs": {"enable_thinking": False},
            },
        )

        async for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            content = delta.content or ""

            if content:
                full_content += content
                if event_queue is not None:
                    await event_queue.put({
                        "event": "response_chunk",
                        "data": {"content": content},
                    })

    except Exception as e:
        logger.exception("LLM 调用失败: %s", e)
        full_content = "抱歉，我的大脑暂时短路了，请稍后再试。"
        if event_queue is not None:
            await event_queue.put({
                "event": "response_chunk",
                "data": {"content": full_content},
            })

    if not full_content:
        full_content = "（未生成任何内容，请检查模型输出或上下文是否异常）"

    return {
        "messages": [AIMessage(content=full_content)],
        "next_action": None,
    }
