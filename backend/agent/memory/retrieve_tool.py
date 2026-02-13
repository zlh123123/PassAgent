"""retrieve_memory 工具：检索用户记忆，注册到 graph tool registry"""
from __future__ import annotations

from agent.graph import register_tool
from agent.state import PassAgentState
from agent.memory.reader import retrieve_memory
from database.connection import SessionLocal


@register_tool("retrieve_memory")
async def retrieve_memory_tool(state: PassAgentState) -> dict:
    """检索用户记忆（全量偏好/约束 + 语义检索事实）。"""
    params = state.get("action_params", {})
    query = params.get("query", "")
    user_id = state.get("user_id", "")

    db = SessionLocal()
    try:
        memories = await retrieve_memory(db, user_id, query)
    finally:
        db.close()

    return {
        "memories": memories,
        "_tool_result": {
            "count": len(memories),
            "types": list({m["memory_type"] for m in memories}),
        },
    }
