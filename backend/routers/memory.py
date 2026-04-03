"""记忆路由（markdown profile 版）。"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session as DBSession

from agent.memory.profile import (
    ensure_memory_profile,
    memory_sections_to_payload,
    parse_memory_profile,
    render_memory_profile,
    save_memory_profile_content,
)
from database.connection import get_db
from database.models import User
from schemas.memory import (
    MemoryItemRequest,
    MemoryOperationResponse,
    MemoryProfileResponse,
    SaveMemoryProfileRequest,
    SaveMemoryProfileResponse,
    UpdateMemoryItemRequest,
)
from utils.deps import get_current_user

router = APIRouter(prefix="/api/memories", tags=["memories"])

_VALID_MEMORY_TYPES = ("PREFERENCE", "FACT", "CONSTRAINT")


def _build_profile_response(profile) -> MemoryProfileResponse:
    sections, _ = parse_memory_profile(profile.content_md)
    return MemoryProfileResponse(
        content_md=profile.content_md,
        sections=memory_sections_to_payload(sections),
        created_at=profile.created_at or "",
        updated_at=profile.updated_at or profile.created_at or "",
        last_used_at=profile.last_used_at,
    )


@router.get("", response_model=MemoryProfileResponse)
def get_memory_profile(
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    profile = ensure_memory_profile(db, user.user_id)
    return _build_profile_response(profile)


@router.put("", response_model=SaveMemoryProfileResponse)
def save_memory_profile(
    body: SaveMemoryProfileRequest,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    profile = ensure_memory_profile(db, user.user_id)
    try:
        _, changed = save_memory_profile_content(db, profile, body.content_md)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return SaveMemoryProfileResponse(message="记忆已保存" if changed else "记忆无变化")


@router.post("/items", response_model=MemoryOperationResponse)
def add_memory_item(
    body: MemoryItemRequest,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    if body.memory_type not in _VALID_MEMORY_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="memory_type 无效")

    content = body.content.strip()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="content 不能为空")

    profile = ensure_memory_profile(db, user.user_id)
    sections, _ = parse_memory_profile(profile.content_md)
    if content in sections[body.memory_type]:
        return MemoryOperationResponse(message="该记忆已存在")

    sections[body.memory_type].append(content)
    _, changed = save_memory_profile_content(db, profile, render_memory_profile(sections))
    return MemoryOperationResponse(message="记忆已添加" if changed else "记忆无变化")


@router.put("/items", response_model=MemoryOperationResponse)
def update_memory_item(
    body: UpdateMemoryItemRequest,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    if body.memory_type not in _VALID_MEMORY_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="memory_type 无效")

    old_content = body.old_content.strip()
    new_content = body.new_content.strip()
    if not old_content or not new_content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="内容不能为空")

    profile = ensure_memory_profile(db, user.user_id)
    sections, _ = parse_memory_profile(profile.content_md)
    items = sections[body.memory_type]
    try:
        index = items.index(old_content)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="记忆不存在")

    items[index] = new_content
    _, changed = save_memory_profile_content(db, profile, render_memory_profile(sections))
    return MemoryOperationResponse(message="记忆已更新" if changed else "记忆无变化")


@router.delete("")
def clear_memory_profile(
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    profile = ensure_memory_profile(db, user.user_id)
    save_memory_profile_content(db, profile, render_memory_profile())
    return {"message": "已清除全部记忆"}


@router.delete("/items", response_model=MemoryOperationResponse)
def delete_memory_item(
    memory_type: str = Query(...),
    content: str = Query(...),
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    if memory_type not in _VALID_MEMORY_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="memory_type 无效")

    profile = ensure_memory_profile(db, user.user_id)
    sections, _ = parse_memory_profile(profile.content_md)
    items = sections[memory_type]
    try:
        items.remove(content.strip())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="记忆不存在")

    _, changed = save_memory_profile_content(db, profile, render_memory_profile(sections))
    return MemoryOperationResponse(message="记忆已删除" if changed else "记忆无变化")
