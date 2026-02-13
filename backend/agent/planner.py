"""Planner 节点：通过 Function Calling 让 LLM 决定下一步动作"""
from __future__ import annotations

import json
from openai import AsyncOpenAI

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from agent.state import PassAgentState
from agent.tools.definitions import TOOL_DEFINITIONS

MAX_LOOPS = 10

PLANNER_SYSTEM_PROMPT = """\
你是 PassAgent 的决策引擎。根据用户请求和已有的工具调用结果，决定下一步该做什么。

## 决策规则

1. **记忆优先**：涉及口令生成或记忆恢复时，若尚未调用 retrieve_memory，必须先调用。
2. **按需调用**：根据中间结果判断是否需要继续，不盲目调用所有工具。
3. **不重复调用**：已调用过的工具不再调用（检查 tool_history）。
4. **跨 skill 组合**：允许一次请求中调用不同类别的工具。
5. **无关请求直接回复**：与口令安全无关的问题，直接调用 respond。
6. **恶意请求拒绝**：涉及攻击、破解他人密码的请求，直接调用 respond 拒绝。
7. **文件感知**：uploaded_files 非空时，仅在生成和恢复场景下调用 multimodal_parse。
8. **信息不足时追问**：用户未提供必要信息（如要检测的密码），直接调用 respond 追问。

## 工具分类

### 强度评估
- zxcvbn_check: 熵值评分（通常第一个调用）
- charset_analyze: 字符组成分析
- keyboard_pattern_check: 键盘连续模式检测
- weak_list_match: 弱口令库匹配
- repetition_check: 重复字符和序列检测
- pcfg_analyze: 结构模式分析
- passgpt_prob: 口令被猜中概率（GPU 模型）
- pass2rule: hashcat 规则变化分析（GPU 模型）
- pinyin_check: 拼音组合检测
- date_pattern_check: 日期模式检测
- personal_info_check: 结合记忆检测个人信息

### 口令生成
- multimodal_parse: 图片/音频转文本关键词
- generate_password: 基于种子词变换生成口令
- passphrase_generate: 助记短语型口令
- pronounceable_generate: 可发音随机口令
- fetch_site_policy: 获取网站密码策略
- strength_verify: 生成口令反向验证强度

### 记忆恢复
- fragment_combine: 片段排列组合
- common_variant_expand: 常见变体扩展
- rule_generate: hashcat 规则生成（GPU 模型）
- date_expand: 日期格式扩展

### 泄露检查
- hibp_password_check: k-Anonymity 查密码泄露
- hibp_email_check: 查邮箱关联泄露事件
- breach_detail: 泄露事件详情
- similar_leak_check: 常见变体批量查泄露

### 图形口令
- graphical_mode: 唤起前端图形口令组件

### 通用
- retrieve_memory: 检索用户记忆（全量偏好 + 语义检索事实）

当你认为信息已经足够生成最终回复时，调用 respond。"""


def _build_context_message(state: PassAgentState) -> str:
    """将当前状态中的关键上下文拼成一条 system 补充消息，供 planner 参考。"""
    parts: list[str] = []

    # 已调用的工具
    if state.get("tool_history"):
        called = [t["tool_name"] for t in state["tool_history"]]
        parts.append(f"已调用的工具: {', '.join(called)}")
        # 最近的工具结果摘要
        for t in state["tool_history"]:
            parts.append(f"  - {t['tool_name']}({json.dumps(t.get('params', {}), ensure_ascii=False)}) → {json.dumps(t.get('result', {}), ensure_ascii=False)}")

    # 记忆
    if state.get("memories"):
        mem_summary = json.dumps(state["memories"], ensure_ascii=False)
        parts.append(f"用户记忆: {mem_summary}")

    # 上传文件
    if state.get("uploaded_files"):
        files_summary = json.dumps(state["uploaded_files"], ensure_ascii=False)
        parts.append(f"上传文件: {files_summary}")

    # 循环计数
    loop = state.get("loop_count", 0)
    parts.append(f"当前循环次数: {loop}/{MAX_LOOPS}")
    if loop >= MAX_LOOPS - 1:
        parts.append("⚠️ 即将达到最大循环次数，请调用 respond 生成最终回复。")

    return "\n".join(parts)


async def planner_node(state: PassAgentState) -> dict:
    """Planner 节点：调用 LLM Function Calling 决定下一步。

    返回对 state 的 partial update：
    - next_action: 工具名 或 "respond"
    - action_params: 传给工具的参数
    - loop_count: +1
    """
    client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

    # 构建消息列表
    messages = [{"role": "system", "content": PLANNER_SYSTEM_PROMPT}]

    # 添加对话历史（从 state.messages 中取 HumanMessage / AIMessage）
    for msg in state["messages"]:
        if hasattr(msg, "type"):
            role = "user" if msg.type == "human" else "assistant"
        else:
            role = msg.get("role", "user")
        content = msg.content if hasattr(msg, "content") else msg.get("content", "")
        messages.append({"role": role, "content": content})

    # 注入上下文
    context = _build_context_message(state)
    if context:
        messages.append({"role": "system", "content": f"[当前状态]\n{context}"})

    # 调用 LLM
    response = await client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        tools=TOOL_DEFINITIONS,
        tool_choice="required",
    )

    choice = response.choices[0]
    tool_call = choice.message.tool_calls[0] if choice.message.tool_calls else None

    if tool_call is None:
        # fallback: 没有工具调用，直接 respond
        return {
            "next_action": "respond",
            "action_params": {"reasoning": "LLM 未返回工具调用，默认生成回复"},
            "loop_count": state.get("loop_count", 0) + 1,
        }

    action_name = tool_call.function.name
    try:
        action_params = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        action_params = {}

    return {
        "next_action": action_name,
        "action_params": action_params,
        "loop_count": state.get("loop_count", 0) + 1,
    }
