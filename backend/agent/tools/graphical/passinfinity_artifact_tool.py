"""passinfinity_artifact 工具：读取用户保存的 PassInfinity 体验结果。"""
from __future__ import annotations

from agent.graph import register_tool
from agent.state import PassAgentState
from database.connection import SessionLocal
from database.models import PassInfinityArtifact
from services.passinfinity_service import artifact_to_response, infer_builder_mode


@register_tool("passinfinity_artifact")
async def passinfinity_artifact_tool(state: PassAgentState) -> dict:
    params = state.get("action_params", {})
    artifact_id = params.get("artifact_id")
    latest = bool(params.get("latest", True))
    user_id = state.get("user_id")

    db = SessionLocal()
    try:
        query = db.query(PassInfinityArtifact).filter(
            PassInfinityArtifact.user_id == user_id
        )
        if artifact_id:
            artifact = query.filter(
                PassInfinityArtifact.artifact_id == artifact_id
            ).first()
        elif latest:
            artifact = query.order_by(PassInfinityArtifact.updated_at.desc()).first()
        else:
            artifact = None
    finally:
        db.close()

    if artifact is None:
        return {
            "_tool_result": {
                "error": "没有找到可读取的 PassInfinity 体验结果。",
                "hint": "可以先去 /lab/passinfinity 生成并保存一条体验结果。",
            }
        }

    data = artifact_to_response(artifact)
    mode = infer_builder_mode(data["normalized_content"])
    data["builder_path"] = f"/lab/passinfinity/{mode}?artifactId={artifact.artifact_id}"
    return {"_tool_result": data}
