"""Planner 节点：通过 Function Calling 让 LLM 决定下一步动作"""
from __future__ import annotations

import json
import logging
from openai import AsyncOpenAI

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from agent.state import PassAgentState
from agent.tools.definitions import TOOL_DEFINITIONS

logger = logging.getLogger(__name__)

MAX_LOOPS = 10

PLANNER_SYSTEM_PROMPT = """\
你是 PassAgent 的决策引擎。根据用户请求和已有的工具调用结果，决定下一步该做什么。

## 决策规则

1. **记忆优先**：涉及口令生成或记忆恢复时，若尚未调用 retrieve_memory，必须先调用。
2. **按需调用**：根据中间结果判断是否需要继续，不盲目调用所有工具。
3. **不重复调用**：相同参数不重复调用同一工具（检查 tool_history）。但同一工具可以用不同参数多次调用。
4. **跨 skill 组合**：允许一次请求中调用不同类别的工具。
5. **无关请求直接回复**：与口令安全无关的问题，直接调用 respond。
6. **恶意请求拒绝**：涉及攻击、破解他人密码的请求，直接调用 respond 拒绝。
7. **文件感知**：uploaded_files 非空时，仅在生成和恢复场景下调用 multimodal_parse。
8. **信息不足时追问**：用户未提供必要信息（如要检测的密码），直接调用 respond 追问。
9. **生成后验证**：生成口令后，应调用口令强度评估反向验证强度。
10. **生成偏好感知**：处理口令生成请求时，读取当前状态中的生成偏好设置：
    - 自动模式（gen_auto_mode=true）：忽略 gen_security_weight，由你根据对话上下文、fetch_site_policy 结果、用户记忆中的 CONSTRAINT 自行决定生成策略和安全档位。用户在对话中的显式要求也纳入决策。
    - 手动模式（gen_auto_mode=false）：**严格**按 gen_security_weight 对应的档位选择生成工具和参数。即使用户在对话中提出不同要求，也按手动设定的档位执行，不覆盖手动设定。

## 工具分类

### 强度评估（8 个）
- zxcvbn_check: 熵值评分（通常第一个调用）
- basic_analysis: 字符组成分析 + 重复模式检测（合并了 charset_analyze 和 repetition_check）
- pattern_detect: 键盘模式 + 拼音组合 + 日期模式统一检测（合并了 keyboard_pattern_check、pinyin_check、date_pattern_check）
- weak_list_match: 弱口令库匹配
- pcfg_analyze: PCFG 结构模式分析
- passgpt_prob: 口令被猜中概率（GPU 模型，待接入）
- pass2rule: hashcat 规则变化分析（GPU 模型，待接入）
- personal_info_check: 结合记忆检测个人信息

### 口令生成（5 个）
- generate_password: 基于种子词变换或纯随机生成安全口令（Python secrets 模块）
- passphrase_generate: 助记短语型口令（xkcdpass/diceware 方法）
- pronounceable_generate: 辅音-元音音节组合的可发音随机口令
- fetch_site_policy: 获取网站密码策略（内置常见站点 + JSON 扩展）
- multimodal_parse: 图片/音频转文本关键词（Qwen-Omni）

### 泄露检查（3 个）
- hibp_password_check: k-Anonymity 查密码泄露（HIBP API）
- hibp_email_check: 邮箱验证与信息查询（Hunter.io API）
- breach_detail: 泄露事件列表或单个事件详情（HIBP Breaches API）

### 口令恢复（2 个）
- fragment_combine: 记忆片段排列组合 + 自动展开年份为多种日期格式
- common_variant_expand: hashcat 规则子集变体扩展（大小写、leet speak、追加数字/符号、反转等）

### 图形口令（1 个）
- graphical_mode: 唤起前端图形口令组件（图片选点/地图选点）

### 通用
- retrieve_memory: 检索用户记忆（全量偏好 + 语义检索事实）

当你认为信息已经足够生成最终回复时，调用 respond。"""


def _build_context_message(state: PassAgentState) -> str:
    """将当前状态中的关键上下文拼成一段文本，合并进唯一的 system message。"""
    parts: list[str] = []

    if state.get("tool_history"):
        called = [t["tool_name"] for t in state["tool_history"]]
        parts.append(f"已调用的工具: {', '.join(called)}")
        for t in state["tool_history"]:
            parts.append(
                f"  - {t['tool_name']}({json.dumps(t.get('params', {}), ensure_ascii=False)})"
                f" → {json.dumps(t.get('result', {}), ensure_ascii=False)}"
            )

    if state.get("memories"):
        mem_summary = json.dumps(state["memories"], ensure_ascii=False)
        parts.append(f"用户记忆: {mem_summary}")

    if state.get("uploaded_files"):
        files_summary = json.dumps(state["uploaded_files"], ensure_ascii=False)
        parts.append(f"上传文件: {files_summary}")

    gen_auto = state.get("gen_auto_mode", True)
    gen_weight = state.get("gen_security_weight", 0.5)
    mode_label = "自动模式（Agent 全权决策）" if gen_auto else f"手动模式（安全性权重 α={gen_weight}）"
    parts.append(f"生成偏好: {mode_label}")

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
    client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    context = _build_context_message(state)
    system_content = PLANNER_SYSTEM_PROMPT
    if context:
        system_content += f"\n\n[当前状态]\n{context}"

    messages = [{"role": "system", "content": system_content}]

    # 追加对话历史
    for msg in state["messages"]:
        if hasattr(msg, "type"):
            role = "user" if msg.type == "human" else "assistant"
        else:
            role = msg.get("role", "user")

        content = msg.content if hasattr(msg, "content") else msg.get("content", "")
        messages.append({"role": role, "content": content})

    logger.info("Planner request: model=%s, message_count=%d", LLM_MODEL, len(messages))

    response = await client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=TOOL_DEFINITIONS,
        tool_choice="auto",
        temperature=0.1,
        max_tokens=1024,
        extra_body={
            "repetition_penalty": 1.05,
            "chat_template_kwargs": {"enable_thinking": False},
        },
    )

    choice = response.choices[0]
    logger.info("Planner raw message: %s", choice.message)

    tool_call = choice.message.tool_calls[0] if choice.message.tool_calls else None

    if tool_call is None:
        logger.warning("Planner returned no tool_calls, fallback to respond.")
        return {
            "next_action": "respond",
            "action_params": {"reasoning": "LLM 未返回工具调用，默认生成回复"},
            "loop_count": state.get("loop_count", 0) + 1,
        }

    action_name = tool_call.function.name
    try:
        action_params = json.loads(tool_call.function.arguments or "{}")
    except json.JSONDecodeError:
        logger.warning("Planner returned malformed tool arguments: %s", tool_call.function.arguments)
        action_params = {}

    logger.info("Planner selected action: %s, params=%s", action_name, action_params)

    return {
        "next_action": action_name,
        "action_params": action_params,
        "loop_count": state.get("loop_count", 0) + 1,
    }
