"""LangGraph 状态图定义：IntentRouter → SkillExecutor → ToolExecutor 循环

新架构流程：
    START → intent_router → (route) → skill_executor → (route) → tool_executor → skill_executor → ...
                               ↓                          ↓
                            respond                     respond → END
"""
from __future__ import annotations

import json
from langgraph.graph import StateGraph, END

from agent.state import PassAgentState
from agent.router import intent_router_node
from agent.skill_executor import skill_executor_node, MAX_LOOPS
from agent.response import respond_node

# 所有已注册的工具名 → 实际执行函数的映射
# 工具函数签名统一为 async def tool_fn(state: PassAgentState) -> dict
# 返回 partial state update，至少包含 tool_history 的追加项
_TOOL_REGISTRY: dict[str, object] = {}


def register_tool(name: str):
    """装饰器：将工具函数注册到全局 registry。"""
    def decorator(fn):
        _TOOL_REGISTRY[name] = fn
        return fn
    return decorator


async def tool_executor_node(state: PassAgentState) -> dict:
    """通用工具执行节点：根据 next_action 分发到具体工具函数。

    执行完后自动更新 todo_list 中当前步的状态。
    """
    action = state.get("next_action")
    params = state.get("action_params", {})
    event_queue = state.get("_event_queue")

    if action is None or action == "respond":
        return {}

    tool_fn = _TOOL_REGISTRY.get(action)
    if tool_fn is None:
        # 工具未实现
        result = {"error": f"工具 {action} 尚未实现"}
        return {
            "tool_history": [{"tool_name": action, "params": params, "result": result}],
        }

    # 执行工具
    try:
        result = await tool_fn(state)
    except Exception as e:
        result = {"error": str(e)}

    # 从 result 中提取 tool_history 追加项
    tool_result = result.get("_tool_result", result)
    tool_history_entry = {
        "tool_name": action,
        "params": params,
        "result": tool_result,
    }

    # 推送 SSE 事件（工具完成）
    if event_queue is not None:
        await event_queue.put({
            "event": "agent_step",
            "data": {"node": action, "summary": tool_result},
        })

    # 合并工具返回的 state 更新
    state_update: dict = {"tool_history": [tool_history_entry]}
    for key in ("memories", "uploaded_files"):
        if key in result:
            state_update[key] = result[key]

    # ---------- 更新 todo_list 中当前步的状态 ----------
    todo_list = state.get("todo_list", [])
    if todo_list:
        updated_todo = []
        for item in todo_list:
            if item.get("status") == "in_progress":
                # 生成结果摘要（截断以节省 token）
                result_str = json.dumps(tool_result, ensure_ascii=False)
                if len(result_str) > 200:
                    result_str = result_str[:200] + "..."
                updated_todo.append({
                    **item,
                    "status": "done",
                    "result_summary": result_str,
                })
            else:
                updated_todo.append(item)
        state_update["todo_list"] = updated_todo

    return state_update


def _route_after_router(state: PassAgentState) -> str:
    """条件路由：intent_router 之后走 respond 还是 skill_executor。"""
    skill = state.get("active_skill")
    action = state.get("next_action")

    # off_topic 或 router 异常 → respond
    if skill == "off_topic" or action == "respond":
        return "respond"

    return "skill_executor"


def _route_after_skill_executor(state: PassAgentState) -> str:
    """条件路由：skill_executor 决策后走 respond 还是 tool_executor。"""
    action = state.get("next_action")
    loop_count = state.get("loop_count", 0)

    if loop_count >= MAX_LOOPS:
        return "respond"

    if action == "respond" or action is None:
        return "respond"

    return "tool_executor"


async def _push_router_step(state: PassAgentState) -> dict:
    """Intent Router 包装节点。"""
    return await intent_router_node(state)


async def _push_skill_executor_step(state: PassAgentState) -> dict:
    """Skill Executor 包装节点。"""
    return await skill_executor_node(state)


def build_graph() -> StateGraph:
    """构建并编译 Agent 状态图。

    流程：
        START → intent_router → (route) → skill_executor → (route) → tool_executor → skill_executor → ...
                                   ↓                          ↓
                                respond                    respond → END
    """
    graph = StateGraph(PassAgentState)

    # 注册节点
    graph.add_node("intent_router", _push_router_step)
    graph.add_node("skill_executor", _push_skill_executor_step)
    graph.add_node("tool_executor", tool_executor_node)
    graph.add_node("respond", respond_node)

    # 入口
    graph.set_entry_point("intent_router")

    # intent_router 之后：off_topic → respond, 其他 → skill_executor
    graph.add_conditional_edges(
        "intent_router",
        _route_after_router,
        {
            "respond": "respond",
            "skill_executor": "skill_executor",
        },
    )

    # skill_executor 之后：respond 或 tool_executor
    graph.add_conditional_edges(
        "skill_executor",
        _route_after_skill_executor,
        {
            "respond": "respond",
            "tool_executor": "tool_executor",
        },
    )

    # tool_executor 执行完后回到 skill_executor 重新决策
    graph.add_edge("tool_executor", "skill_executor")

    # respond 之后结束
    graph.add_edge("respond", END)

    return graph.compile()


# ---------- 注册所有工具（必须在 build_graph 之前） ----------
# 通用
import agent.memory.retrieve_tool  # noqa: F401, E402

# 强度评估
import agent.tools.strength.zxcvbn_tool  # noqa: F401, E402
import agent.tools.strength.basic_analysis_tool  # noqa: F401, E402
import agent.tools.strength.pattern_detect_tool  # noqa: F401, E402
import agent.tools.strength.pcfg_tool  # noqa: F401, E402
import agent.tools.strength.weak_list_tool  # noqa: F401, E402
import agent.tools.strength.personal_info_tool  # noqa: F401, E402
import agent.tools.strength.passtsl_tool  # noqa: F401, E402
import agent.tools.strength.pass2rule_tool  # noqa: F401, E402

# 口令生成
import agent.tools.generation.generate_tool  # noqa: F401, E402
import agent.tools.generation.passphrase_tool  # noqa: F401, E402
import agent.tools.generation.pronounceable_tool  # noqa: F401, E402
import agent.tools.generation.site_policy_tool  # noqa: F401, E402
import agent.tools.generation.multimodal_tool  # noqa: F401, E402

# 泄露检查
import agent.tools.leak.hibp_password_tool  # noqa: F401, E402
import agent.tools.leak.hibp_email_tool  # noqa: F401, E402
import agent.tools.leak.breach_detail_tool  # noqa: F401, E402

# 口令恢复
import agent.tools.recovery.fragment_tool  # noqa: F401, E402
import agent.tools.recovery.variant_tool  # noqa: F401, E402

# 图形口令
import agent.tools.graphical.graphical_mode_tool  # noqa: F401, E402
import agent.tools.graphical.passinfinity_artifact_tool  # noqa: F401, E402

# 编译好的 graph 实例，供 runner 直接调用
agent_graph = build_graph()
