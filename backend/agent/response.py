"""Respond 节点：汇总工具结果，生成最终用户回复（流式）"""
from __future__ import annotations

import json
import logging
from openai import AsyncOpenAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from agent.state import PassAgentState

logger = logging.getLogger(__name__)

def _build_respond_system_prompt(state: PassAgentState) -> str:
    """构建增强版 System Prompt，强化专家人设和输出结构。"""
    tool_history = state.get("tool_history", [])
    tool_count = len(tool_history)
    
    # 基础人设
    base_persona = """
你叫 PassAgent，是用户的**个人口令安全审计专家**。你的核心职责是评估风险、发现隐患并提供加固建议。
你的回答必须：
1. **准确严谨**：基于工具返回的数据说话，不要编造未检测到的风险。
2. **通俗易懂**：将技术术语（如"哈希碰撞"、"熵值"）转化为用户能懂的语言。
3. **安全第一**：如果工具返回了敏感信息（如明文密码），在回复中应进行打码处理（如 `P***d`），除非用户明确要求显示。
"""

    # 动态任务指令
    if tool_count == 0:
        task_instruction = """
当前状态：**闲聊或意图识别阶段**
- 如果用户是在打招呼，请热情回应并简述你能做什么（如：检测密码强度、生成抗破解规则、查询泄露库）。
- 如果用户的问题超出了"口令安全"范畴，请礼貌地将话题引导回你的专业领域。
- 拒绝处理任何非法的破解请求（如"帮我破解隔壁的WiFi"）。
"""
    else:
        task_instruction = """
当前状态：**分析报告生成阶段**
请根据下方的 `<tool_outputs>` 生成回复。遵循以下格式：

### 1. 核心结论
用一句话概括结果（例如："检测通过，您的密码强度极高" 或 "警告：发现该密码在3个泄露库中出现"）。

### 2. 详细分析
- 解读工具返回的数据，不要直接罗列 JSON 字段。
- 如果涉及评分，请用直观描述（如 🔴高危、🟡中等、🟢安全）。
- 解释为什么会得出这个结论（例如："因为它由纯数字组成"）。

### 3. 后续建议
- 针对当前情况给出 2-3 条具体行动建议。
- 建议必须具有可操作性。
"""

    return f"{base_persona}\n{task_instruction}"


def _build_tool_context(state: PassAgentState) -> str:
    """将工具结果和记忆格式化为结构清晰的 XML 上下文，便于 Qwen 理解。"""
    
    context_parts = []

    # 1. 处理工具调用历史
    if state.get("tool_history"):
        tools_str = []
        for i, t in enumerate(state["tool_history"], 1):
            tool_name = t["tool_name"]
            # 简化 result，防止过长 JSON 撑爆上下文
            result_str = json.dumps(t.get("result", {}), ensure_ascii=False)
            status = "成功" if t.get("status") != "error" else "失败"
            
            tools_str.append(f"""
<tool_execution id="{i}">
    <name>{tool_name}</name>
    <status>{status}</status>
    <result>{result_str}</result>
</tool_execution>""")
        
        context_parts.append("<tool_outputs>\n" + "\n".join(tools_str) + "\n</tool_outputs>")

    # 2. 处理长期记忆 (User Profile)
    if state.get("memories"):
        mem_str = []
        for mem in state["memories"]:
            m_type = mem.get('memory_type', 'INFO')
            content = mem.get('content', '')
            mem_str.append(f"- [{m_type}] {content}")
        
        context_parts.append("<user_profile>\n" + "\n".join(mem_str) + "\n</user_profile>")

    return "\n\n".join(context_parts)


async def respond_node(state: PassAgentState) -> dict:
    """Respond 节点：流式生成最终回复。"""
    client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    event_queue = state.get("_event_queue")

    # 1. 构建 System Prompt
    system_content = _build_respond_system_prompt(state)
    
    # 2. 构建上下文数据 (工具结果 + 记忆)
    context_content = _build_tool_context(state)
    
    # 3. 组装 Messages
    # 这里的技巧是：把 System Prompt 放在最前，把工具数据作为 System Message 紧随其后
    # 或者作为 User Message 的补充。对于 Qwen，分开放 System 效果较好。
    messages = [
        {"role": "system", "content": system_content},
    ]

    # 如果有工具上下文，作为辅助 System 信息插入
    if context_content:
        messages.append({
            "role": "system", 
            "content": f"请基于以下上下文数据回答用户：\n{context_content}"
        })

    # 追加历史对话
    for msg in state["messages"]:
        if hasattr(msg, "type"):
            role = "user" if msg.type == "human" else "assistant"
        else:
            role = msg.get("role", "user")
        content = msg.content if hasattr(msg, "content") else str(msg.get("content", ""))
        messages.append({"role": role, "content": content})

    # 流式调用 LLM
    try:
        stream = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            stream=True,
            temperature=0.7, # 稍微降低温度，保证分析的严谨性
            max_tokens=2048,
        )

        full_content = ""
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            # 兼容 DeepSeek/Qwen 的不同字段
            content = delta.content or getattr(delta, "reasoning_content", None) or ""
            
            if content:
                full_content += content
                if event_queue is not None:
                    await event_queue.put({
                        "event": "response_chunk",
                        "data": {"content": content},
                    })
    except Exception as e:
        logger.error(f"LLM调用失败: {e}")
        full_content = "抱歉，我的大脑暂时短路了，请检查后台日志。"
        if event_queue:
            await event_queue.put({"event": "response_chunk", "data": {"content": full_content}})

    if not full_content:
        full_content = "（未生成任何内容，请检查工具输出是否过长导致截断）"

    return {
        "messages": [AIMessage(content=full_content)],
        "next_action": None,
    }