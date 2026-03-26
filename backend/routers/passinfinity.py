"""PassInfinity 独立体验页 API。"""
from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from database.connection import get_db
from database.models import PassInfinityArtifact, User
from schemas.passinfinity import (
    PassInfinityAnalyzeResponse,
    PassInfinityArtifactListResponse,
    PassInfinityArtifactResponse,
    PassInfinityDraftRequest,
    PassInfinityPolicyResponse,
)
from services.passinfinity_service import (
    analyze_draft,
    artifact_to_response,
    get_default_policy,
)
from utils.deps import get_current_user
from utils.timezone import beijing_now_iso

router = APIRouter(prefix="/api/passinfinity", tags=["passinfinity"])


@router.get("/policy", response_model=PassInfinityPolicyResponse)
def get_policy():
    return PassInfinityPolicyResponse(policy=get_default_policy())


@router.post("/validate", response_model=PassInfinityAnalyzeResponse)
def validate_draft(body: PassInfinityDraftRequest):
    result = analyze_draft(body.model_dump())
    return PassInfinityAnalyzeResponse(**result)


@router.post("/encode", response_model=PassInfinityAnalyzeResponse)
def encode_draft(body: PassInfinityDraftRequest):
    result = analyze_draft(body.model_dump())
    return PassInfinityAnalyzeResponse(**result)


@router.post("/artifacts", response_model=PassInfinityArtifactResponse)
def create_artifact(
    body: PassInfinityDraftRequest,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    result = analyze_draft(body.model_dump())
    if not result["policy_result"]["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前体验结果未通过基础校验，暂时不能保存。",
        )

    now = beijing_now_iso()
    artifact = PassInfinityArtifact(
        artifact_id=uuid.uuid4().hex,
        user_id=user.user_id,
        title=result["normalized_content"]["title"],
        content_json=json.dumps(result["normalized_content"], ensure_ascii=False),
        encoded_text=result["encoded_text"],
        policy_result_json=json.dumps(result["policy_result"], ensure_ascii=False),
        created_at=now,
        updated_at=now,
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return PassInfinityArtifactResponse(**artifact_to_response(artifact))


@router.get("/artifacts", response_model=PassInfinityArtifactListResponse)
def list_artifacts(
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    artifacts = (
        db.query(PassInfinityArtifact)
        .filter(PassInfinityArtifact.user_id == user.user_id)
        .order_by(PassInfinityArtifact.updated_at.desc())
        .all()
    )
    return PassInfinityArtifactListResponse(
        artifacts=[PassInfinityArtifactResponse(**artifact_to_response(item)) for item in artifacts]
    )


@router.get("/artifacts/{artifact_id}", response_model=PassInfinityArtifactResponse)
def get_artifact(
    artifact_id: str,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    artifact = (
        db.query(PassInfinityArtifact)
        .filter(
            PassInfinityArtifact.artifact_id == artifact_id,
            PassInfinityArtifact.user_id == user.user_id,
        )
        .first()
    )
    if artifact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="体验结果不存在")
    return PassInfinityArtifactResponse(**artifact_to_response(artifact))
