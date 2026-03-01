"""LangGraph 状态图定义：Planner → Router → Tool/Respond 循环"""
from __future__ import annotations

from langgraph.graph import StateGraph, END

from agent.state import PassAgentState
from agent.planner import planner_node, MAX_LOOPS
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
    """通用工具执行节点：根据 next_action 分发到具体工具函数。"""
    action = state.get("next_action")
    params = state.get("action_params", {})
    event_queue = state.get("_event_queue")

    if action is None or action == "respond":
        return {}

    tool_fn = _TOOL_REGISTRY.get(action)
    if tool_fn is None:
        # 工具未实现，记录到 tool_history 并继续
        result = {"error": f"工具 {action} 尚未实现"}
        return {
            "tool_history": [{"tool_name": action, "params": params, "result": result}],
        }

    # 推送 agent_step 事件（工具开始）— planner 的决策步骤已在 router 前推送
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

    # 推送 agent_step 事件（工具完成）
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

    return state_update


def _route_after_planner(state: PassAgentState) -> str:
    """条件路由：planner 决策后走 respond 还是 tool_executor。"""
    action = state.get("next_action")
    loop_count = state.get("loop_count", 0)

    # 超过最大循环次数，强制 respond
    if loop_count >= MAX_LOOPS:
        return "respond"

    if action == "respond" or action is None:
        return "respond"

    return "tool_executor"


async def _push_planner_step(state: PassAgentState) -> dict:
    """Planner 包装节点：先执行 planner，再推送 agent_step SSE 事件。"""
    result = await planner_node(state)
    event_queue = state.get("_event_queue")

    if event_queue is not None:
        action = result.get("next_action", "respond")
        reasoning = result.get("action_params", {}).get("reasoning", "")
        await event_queue.put({
            "event": "agent_step",
            "data": {
                "node": "planner",
                "action": action,
                "reasoning": reasoning,
            },
        })

    return result


def build_graph() -> StateGraph:
    """构建并编译 Agent 状态图。

    流程：
        START → planner → (router) → tool_executor → planner → ...
                                   → respond → END
    """
    graph = StateGraph(PassAgentState)

    # 注册节点
    graph.add_node("planner", _push_planner_step)
    graph.add_node("tool_executor", tool_executor_node)
    graph.add_node("respond", respond_node)

    # 入口
    graph.set_entry_point("planner")

    # 条件边：planner 之后根据 next_action 路由
    graph.add_conditional_edges(
        "planner",
        _route_after_planner,
        {
            "respond": "respond",
            "tool_executor": "tool_executor",
        },
    )

    # tool_executor 执行完后回到 planner 重新决策
    graph.add_edge("tool_executor", "planner")

    # respond 之后结束
    graph.add_edge("respond", END)

    return graph.compile()


# ---------- 注册所有工具（必须在 build_graph 之前） ----------
import agent.memory.retrieve_tool  # noqa: F401, E402
import agent.tools.strength.keyboard_tool  # noqa: F401, E402
import agent.tools.strength.zxcvbn_tool  # noqa: F401, E402
import agent.tools.strength.charset_tool  # noqa: F401, E402
import agent.tools.strength.weak_list_tool  # noqa: F401, E402
import agent.tools.strength.repetition_tool  # noqa: F401, E402
import agent.tools.strength.pcfg_tool  # noqa: F401, E402
import agent.tools.strength.pinyin_tool  # noqa: F401, E402
import agent.tools.strength.date_tool  # noqa: F401, E402
import agent.tools.strength.personal_info_tool  # noqa: F401, E402
import agent.tools.leak.hibp_password_tool  # noqa: F401, E402

# 编译好的 graph 实例，供 runner 直接调用
agent_graph = build_graph()
