"""Skill Executor 节点：基于 TODO List 逐步执行，仅加载当前 skill 的工具

替代原 planner_node，核心改进：
1. 每次只加载当前 skill 的工具定义（3~10 个，而非全部 19 个）
2. 有全局 TODO List 视角，知道当前在第几步
3. 可根据工具执行结果微调剩余计划
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from openai import AsyncOpenAI

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from agent.graphical_intent import infer_graphical_mode
from agent.state import PassAgentState
from agent.skills import SKILL_REGISTRY, load_skill_prompt
from agent.tools.definitions import get_tools_for_skill

logger = logging.getLogger(__name__)

MAX_LOOPS = 12
MAX_DUPLICATE_RETRIES = 2
_PASSWORD_CANDIDATE_RE = re.compile(
    r"[A-Za-z0-9`~!@#$%^&*()_\-+={}\[\]|\\:;\"'<>,.?/]{4,}"
)
_COMMON_NON_PASSWORD_TOKENS = {
    "passagent",
    "passinfinity",
    "pass2rule",
    "passtsl",
    "zxcvbn",
    "pcfg",
    "pattern",
    "graph",
    "password",
    "http",
    "https",
    "api",
    "agent",
}
_FORCED_STRENGTH_TOOLS = {
    "zxcvbn_check",
    "basic_analysis",
    "pattern_detect",
    "weak_list_match",
    "pcfg_analyze",
    "personal_info_check",
    "passtsl_prob",
    "pass2rule",
}

# ---------------------------------------------------------------------------
# LangGraph 消息类型 → OpenAI 角色映射
# ---------------------------------------------------------------------------
TYPE_ROLE_MAP = {
    "human": "user",
    "ai": "assistant",
    "system": "system",
    "tool": "tool",
}


def _latest_user_text(state: PassAgentState) -> str:
    for msg in reversed(state["messages"]):
        msg_type = getattr(msg, "type", None)
        role = msg.get("role") if isinstance(msg, dict) else None
        if msg_type == "human" or role == "user":
            content = msg.content if hasattr(msg, "content") else msg.get("content", "")
            return str(content or "").strip()
    return ""


def _message_role(msg) -> str:
    if hasattr(msg, "type"):
        return TYPE_ROLE_MAP.get(msg.type, "user")
    return msg.get("role", "user") if isinstance(msg, dict) else "user"


def _message_content(msg) -> str:
    return str(msg.content if hasattr(msg, "content") else msg.get("content", "") or "")


def _is_plausible_password_token(token: str) -> bool:
    lowered = token.strip("`'\"“”‘’「」『』.,，。:：;；()[]{}").lower()
    if not lowered or lowered in _COMMON_NON_PASSWORD_TOKENS:
        return False
    if lowered.startswith(("http", "www.")):
        return False
    return True


def _select_password_candidate(candidates: list[str]) -> str:
    cleaned = [
        item.strip("`'\"“”‘’「」『』.,，。:：;；()[]{}")
        for item in candidates
    ]
    plausible = [item for item in cleaned if _is_plausible_password_token(item)]
    if not plausible:
        return ""

    with_digit_or_symbol = [
        item for item in plausible
        if any(ch.isdigit() for ch in item)
        or any(not ch.isalnum() for ch in item)
    ]
    return (with_digit_or_symbol or plausible)[-1]


def _extract_password_candidate(text: str) -> str:
    quoted = re.search(r"[\"'“”‘’「」『』](.+?)[\"'“”‘’「」『』]", text)
    if quoted:
        candidate = quoted.group(1).strip()
        if _is_plausible_password_token(candidate):
            return candidate

    candidates = _PASSWORD_CANDIDATE_RE.findall(text)
    return _select_password_candidate(candidates)


def _extract_password_from_tool_history(state: PassAgentState) -> str:
    for item in reversed(state.get("tool_history", [])):
        params = item.get("params", {})
        result = item.get("result", {})
        for value in (
            params.get("password"),
            result.get("input_password") if isinstance(result, dict) else None,
        ):
            if isinstance(value, str) and _is_plausible_password_token(value):
                return value
    return ""


def _extract_password_for_strength(state: PassAgentState) -> str:
    latest = _extract_password_candidate(_latest_user_text(state))
    if latest:
        return latest

    from_tools = _extract_password_from_tool_history(state)
    if from_tools:
        return from_tools

    messages = list(state.get("messages", []))
    previous_messages = messages[:-1] if messages else []
    for role in ("user", "assistant"):
        for msg in reversed(previous_messages):
            if _message_role(msg) != role:
                continue
            candidate = _extract_password_candidate(_message_content(msg))
            if candidate:
                return candidate
    return ""


def _maybe_forced_strength_action(
    state: PassAgentState,
    step_skill: str,
    current_step: dict,
    todo_list: list[dict],
) -> dict | None:
    """Strength assessment follows its planned evidence chain deterministically."""
    if step_skill != "strength-assessment":
        return None

    tool_name = current_step.get("tool_name")
    if not tool_name:
        return None

    if tool_name == "respond":
        return {
            "next_action": "respond",
            "action_params": {"reasoning": current_step.get("description", "")},
            "loop_count": state.get("loop_count", 0) + 1,
            "todo_list": todo_list,
        }

    latest_text = _latest_user_text(state)
    if tool_name == "retrieve_memory":
        return {
            "next_action": "retrieve_memory",
            "action_params": {"query": latest_text or "用户口令偏好、个人信息和约束"},
            "loop_count": state.get("loop_count", 0) + 1,
            "todo_list": todo_list,
        }

    if tool_name in _FORCED_STRENGTH_TOOLS:
        password = _extract_password_for_strength(state)
        if not password:
            return {
                "next_action": "respond",
                "action_params": {"reasoning": "用户没有提供可评估的具体口令"},
                "loop_count": state.get("loop_count", 0) + 1,
                "todo_list": todo_list,
            }
        return {
            "next_action": tool_name,
            "action_params": {"password": password},
            "loop_count": state.get("loop_count", 0) + 1,
            "todo_list": todo_list,
        }

    return None


def _recent_texts(state: PassAgentState, limit: int = 6) -> str:
    texts: list[str] = []
    for msg in state["messages"][-limit:]:
        content = msg.content if hasattr(msg, "content") else msg.get("content", "")
        text = str(content or "").strip()
        if text:
            texts.append(text.lower())
    return "\n".join(texts)


def _maybe_short_circuit_graphical_mode(
    state: PassAgentState,
    step_skill: str,
    current_step: dict,
    todo_list: list[dict],
) -> dict | None:
    if step_skill != "graphical-mode":
        return None

    latest_text = _latest_user_text(state).lower()
    recent_context = _recent_texts(state)
    if not latest_text:
        return None

    wants_artifact = "passinfinity" in latest_text and any(
        keyword in latest_text
        for keyword in ("解释", "解读", "分析", "看看", "刚保存", "保存的", "最近保存", "方案")
    )

    if wants_artifact:
        return {
            "next_action": "passinfinity_artifact",
            "action_params": {"latest": True},
            "loop_count": state.get("loop_count", 0) + 1,
            "todo_list": todo_list,
        }

    mode = infer_graphical_mode(latest_text)
    if mode is None and any(keyword in latest_text for keyword in ("开链接", "打开链接", "链接", "开页面", "打开页面", "跳转", "进入页面", "去看看")):
        mode = infer_graphical_mode(recent_context)
    if mode is None:
        mode = infer_graphical_mode((current_step.get("description", "") or "").lower())
    if mode is None:
        mode = "select"

    return {
        "next_action": "graphical_mode",
        "action_params": {"mode": mode},
        "loop_count": state.get("loop_count", 0) + 1,
        "todo_list": todo_list,
    }


def _make_call_key(tool_name: str, params: dict) -> str:
    """生成工具调用的唯一指纹"""
    param_str = json.dumps(params, sort_keys=True, ensure_ascii=False)
    return f"{tool_name}::{hashlib.md5(param_str.encode()).hexdigest()}"


def _build_existing_keys(state: PassAgentState) -> set[str]:
    """从 tool_history 中提取所有已调用的指纹集合"""
    keys = set()
    for t in state.get("tool_history", []):
        keys.add(_make_call_key(t["tool_name"], t.get("params", {})))
    return keys


def _build_todo_progress(todo_list: list[dict], current_idx: int) -> str:
    """构建 TODO 进度展示文本"""
    if not todo_list:
        return ""

    lines = ["## 当前计划进度"]
    for i, item in enumerate(todo_list):
        status = item.get("status", "pending")
        desc = item.get("description", "")
        summary = item.get("result_summary", "")

        if status == "done":
            prefix = "[DONE]"
            suffix = f" → {summary}" if summary else ""
        elif status == "skipped":
            prefix = "[SKIP]"
            suffix = f" → {summary}" if summary else ""
        elif i == current_idx:
            prefix = "[>>  ]"
            suffix = "  ← 当前步"
        else:
            prefix = "[    ]"
            suffix = ""

        lines.append(f"{prefix} {item.get('step_id', i+1)}. {desc}{suffix}")

    return "\n".join(lines)


def _build_context_message(state: PassAgentState, current_step: dict) -> str:
    """构建当前状态上下文（比原 planner 更精简）"""
    parts: list[str] = []

    # TODO 进度
    todo_list = state.get("todo_list", [])
    current_idx = next(
        (i for i, t in enumerate(todo_list) if t.get("status") == "in_progress"),
        0,
    )
    progress = _build_todo_progress(todo_list, current_idx)
    if progress:
        parts.append(progress)

    # 已调用工具（精简版，只显示工具名和摘要）
    if state.get("tool_history"):
        parts.append("## 已调用工具")
        seen_sigs: list[str] = []
        for t in state["tool_history"]:
            call_sig = (
                f"{t['tool_name']}"
                f"({json.dumps(t.get('params', {}), sort_keys=True, ensure_ascii=False)})"
            )
            seen_sigs.append(call_sig)
            result_str = json.dumps(t.get("result", {}), ensure_ascii=False)
            if len(result_str) > 500:
                result_str = result_str[:500] + "...(truncated)"
            parts.append(f"  ✅ {call_sig} → {result_str}")
        parts.append(f"⛔ 禁止重复: {seen_sigs}")

    # 用户记忆
    if state.get("memories"):
        prefs = [
            ("[自动] " if m.get("source") == "AUTO" else "") + m["content"]
            for m in state["memories"] if m.get("memory_type") == "PREFERENCE"
        ]
        constraints = [
            ("[自动] " if m.get("source") == "AUTO" else "") + m["content"]
            for m in state["memories"] if m.get("memory_type") == "CONSTRAINT"
        ]
        facts = [
            (
                ("[待确认] " if m.get("is_stale") else "")
                + ("[自动] " if m.get("source") == "AUTO" else "")
                + m["content"]
            )
            for m in state["memories"] if m.get("memory_type") == "FACT"
        ]
        mem_parts = []
        if prefs:
            mem_parts.append("偏好: " + "; ".join(prefs))
        if constraints:
            mem_parts.append("约束: " + "; ".join(constraints))
        if facts:
            mem_parts.append("个人事实: " + "; ".join(facts))
        parts.append("用户记忆:\n" + "\n".join(mem_parts))

    # 上传文件
    if state.get("uploaded_files"):
        files_summary = json.dumps(state["uploaded_files"], ensure_ascii=False)
        parts.append(f"上传文件: {files_summary}")

    # 生成偏好
    gen_auto = state.get("gen_auto_mode", True)
    gen_weight = state.get("gen_security_weight", 0.5)
    if not gen_auto:
        parts.append(f"生成偏好: 手动模式（安全性权重 α={gen_weight}）")

    # 循环计数
    loop = state.get("loop_count", 0)
    parts.append(f"当前循环: {loop}/{MAX_LOOPS}")
    if loop >= MAX_LOOPS - 2:
        parts.append("⚠️ 即将达到最大循环次数，请尽快调用 respond。")

    return "\n".join(parts)


def _build_messages(
    state: PassAgentState,
    skill_prompt: str,
    current_step: dict,
    extra_hints: list[str] | None = None,
) -> list[dict]:
    """构建发送给 LLM 的 messages 列表。

    system = skill markdown + 当前状态上下文
    """
    context = _build_context_message(state, current_step)

    # 核心指令：skill 专属 prompt + 当前步骤指引
    system_content = skill_prompt
    system_content += f"\n\n## 当前步骤\n你现在需要执行: {current_step.get('description', '')}"
    suggested_tool = current_step.get("tool_name")
    if suggested_tool:
        system_content += f"\n建议工具: {suggested_tool}（你可以根据实际情况调整）"

    system_content += "\n\n## 通用规则\n"
    system_content += "- 相同工具+相同参数不重复调用\n"
    system_content += "- 信息充足时立即调用 respond\n"
    system_content += "- 中文种子词/片段必须转为拼音或英文再传入工具\n"

    if context:
        system_content += f"\n\n[当前状态]\n{context}"

    if extra_hints:
        system_content += "\n\n[去重警告 - 必须遵守]\n" + "\n".join(extra_hints)

    messages: list[dict] = [{"role": "system", "content": system_content}]

    # 追加对话历史
    for msg in state["messages"]:
        if hasattr(msg, "type"):
            role = TYPE_ROLE_MAP.get(msg.type, "user")
        else:
            role = msg.get("role", "user")

        content = msg.content if hasattr(msg, "content") else msg.get("content", "")
        if not content or role == "system":
            continue
        messages.append({"role": role, "content": content})

    return messages


async def _call_llm(messages: list[dict], tools: list[dict], client: AsyncOpenAI) -> dict:
    """封装一次 LLM 调用（仅传入当前 skill 的工具）"""
    if LLM_MODEL == "deepseek-chat":
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            tools=tools,
            temperature=0.1,
            max_tokens=2048,
        )
    else:
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.1,
            max_tokens=2048,
            extra_body={
                "repetition_penalty": 1.05,
                "chat_template_kwargs": {"enable_thinking": False},
            },
        )
    return response


def _find_current_step(todo_list: list[dict]) -> tuple[int, dict | None]:
    """找到第一个 pending 的步骤，返回 (index, step)"""
    for i, item in enumerate(todo_list):
        if item.get("status") == "pending":
            return i, item
    return -1, None


def _resolve_step_skill(step: dict, active_skill: str) -> str:
    """确定当前步骤应该使用哪个 skill"""
    step_skill = step.get("skill")
    if step_skill and step_skill in SKILL_REGISTRY:
        return step_skill
    if active_skill and active_skill in SKILL_REGISTRY:
        return active_skill
    # 降级：返回第一个 skill
    return next(iter(SKILL_REGISTRY))


async def skill_executor_node(state: PassAgentState) -> dict:
    """Skill Executor 节点：按 TODO List 逐步执行。

    返回对 state 的 partial update：
    - next_action: 工具名 或 "respond"
    - action_params: 传给工具的参数
    - loop_count: +1
    - todo_list: 更新后的 TODO List（当前步标为 in_progress）
    """
    client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    try:
        event_queue = state.get("_event_queue")
        active_skill = state.get("active_skill", "")
        todo_list = list(state.get("todo_list", []))  # 浅拷贝以便修改

        # ---------- 找到当前待执行步骤 ----------
        current_idx, current_step = _find_current_step(todo_list)

        if current_step is None:
            # 所有步骤已完成，走 respond
            logger.info("All TODO steps done, routing to respond")
            return {
                "next_action": "respond",
                "action_params": {"reasoning": "所有计划步骤已完成"},
                "loop_count": state.get("loop_count", 0) + 1,
            }

        # 标记当前步为 in_progress
        todo_list[current_idx] = {**current_step, "status": "in_progress"}

        # ---------- 确定当前 skill 并加载资源 ----------
        step_skill = _resolve_step_skill(current_step, active_skill)
        skill_prompt = load_skill_prompt(step_skill)
        skill_tools = get_tools_for_skill(step_skill)

        logger.info(
            "SkillExecutor: step=%d/%d, skill=%s, tools=%d, description=%s",
            current_idx + 1, len(todo_list), step_skill,
            len(skill_tools), current_step.get("description", ""),
        )

        shortcut_result = _maybe_short_circuit_graphical_mode(
            state, step_skill, current_step, todo_list
        )
        if shortcut_result is not None:
            logger.info(
                "SkillExecutor shortcut for graphical-mode: %s, params=%s",
                shortcut_result["next_action"],
                shortcut_result["action_params"],
            )
            if event_queue is not None:
                await event_queue.put({
                    "event": "agent_step",
                    "data": {
                        "node": "skill_executor",
                        "action": shortcut_result["next_action"],
                        "reasoning": current_step.get("description", "") or "命中图形口令快捷规则",
                        "step_index": current_idx + 1,
                        "total_steps": len(todo_list),
                    },
                })
            return shortcut_result

        forced_strength_result = _maybe_forced_strength_action(
            state, step_skill, current_step, todo_list
        )
        if forced_strength_result is not None:
            logger.info(
                "SkillExecutor forced strength step: %s, params=%s",
                forced_strength_result["next_action"],
                forced_strength_result["action_params"],
            )
            if event_queue is not None:
                await event_queue.put({
                    "event": "agent_step",
                    "data": {
                        "node": "skill_executor",
                        "action": forced_strength_result["next_action"],
                        "reasoning": current_step.get("description", ""),
                        "step_index": current_idx + 1,
                        "total_steps": len(todo_list),
                    },
                })
            return forced_strength_result

        # ---------- 已调用指纹集合（去重用） ----------
        existing_keys = _build_existing_keys(state)

        # ---------- 带重试的决策循环 ----------
        duplicate_retries = 0
        extra_hints: list[str] = []

        while duplicate_retries <= MAX_DUPLICATE_RETRIES:
            messages = _build_messages(state, skill_prompt, current_step, extra_hints)
            logger.info(
                "SkillExecutor LLM call: message_count=%d, tool_count=%d, retry=%d",
                len(messages), len(skill_tools), duplicate_retries,
            )

            try:
                response = await _call_llm(messages, skill_tools, client)
            except Exception as e:
                logger.error("SkillExecutor LLM call failed: %s", e)
                # 标记当前步为 skipped
                todo_list[current_idx] = {
                    **todo_list[current_idx],
                    "status": "skipped",
                    "result_summary": f"LLM 调用失败: {e}",
                }
                return {
                    "next_action": "respond",
                    "action_params": {"reasoning": f"LLM 调用异常: {e}，强制生成回复"},
                    "loop_count": state.get("loop_count", 0) + 1,
                    "todo_list": todo_list,
                }

            choice = response.choices[0]
            tool_call = (
                choice.message.tool_calls[0] if choice.message.tool_calls else None
            )

            # ---- 无工具调用 → respond ----
            if tool_call is None:
                logger.warning("SkillExecutor returned no tool_calls, fallback to respond")
                todo_list[current_idx] = {
                    **todo_list[current_idx],
                    "status": "done",
                    "result_summary": "LLM 选择直接回复",
                }
                return {
                    "next_action": "respond",
                    "action_params": {"reasoning": "LLM 未返回工具调用，生成回复"},
                    "loop_count": state.get("loop_count", 0) + 1,
                    "todo_list": todo_list,
                }

            action_name = tool_call.function.name
            try:
                action_params = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                logger.warning("Malformed tool arguments: %s", tool_call.function.arguments)
                action_params = {}

            # ---- respond 不需要去重 ----
            if action_name == "respond":
                logger.info("SkillExecutor selected respond")
                todo_list[current_idx] = {
                    **todo_list[current_idx],
                    "status": "done",
                    "result_summary": "决定汇总回复",
                }
                return {
                    "next_action": "respond",
                    "action_params": action_params,
                    "loop_count": state.get("loop_count", 0) + 1,
                    "todo_list": todo_list,
                }

            # ---- 去重检查 ----
            call_key = _make_call_key(action_name, action_params)

            if call_key not in existing_keys:
                # 正常返回
                logger.info("SkillExecutor selected: %s, params=%s", action_name, action_params)

                # 推送 SSE 事件
                if event_queue is not None:
                    await event_queue.put({
                        "event": "agent_step",
                        "data": {
                            "node": "skill_executor",
                            "action": action_name,
                            "reasoning": current_step.get("description", ""),
                            "step_index": current_idx + 1,
                            "total_steps": len(todo_list),
                        },
                    })

                return {
                    "next_action": action_name,
                    "action_params": action_params,
                    "loop_count": state.get("loop_count", 0) + 1,
                    "todo_list": todo_list,
                }

            # ---- 重复调用 ----
            duplicate_retries += 1
            logger.warning(
                "SkillExecutor duplicate (%d/%d): %s(%s)",
                duplicate_retries, MAX_DUPLICATE_RETRIES,
                action_name, json.dumps(action_params, ensure_ascii=False),
            )
            extra_hints.append(
                f"⚠️ {action_name}({json.dumps(action_params, ensure_ascii=False)}) 已调用过。"
                f"请选择不同的工具，或调用 respond。"
            )

        # ---- 重试耗尽 ----
        logger.warning("SkillExecutor max duplicate retries, forcing respond")
        todo_list[current_idx] = {
            **todo_list[current_idx],
            "status": "skipped",
            "result_summary": "重复调用超限，跳过",
        }
        return {
            "next_action": "respond",
            "action_params": {
                "reasoning": f"工具 {action_name} 重复调用 {duplicate_retries} 次，强制回复"
            },
            "loop_count": state.get("loop_count", 0) + 1,
            "todo_list": todo_list,
        }
    finally:
        await client.close()
