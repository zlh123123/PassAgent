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
    PromoteMemoryItemRequest,
    SaveMemoryProfileRequest,
    SaveMemoryProfileResponse,
    UpdateMemoryItemRequest,
)
from utils.deps import get_current_user

router = APIRouter(prefix="/api/memories", tags=["memories"])

_VALID_MEMORY_TYPES = ("PREFERENCE", "FACT", "CONSTRAINT")
_VALID_MEMORY_SOURCES = ("MANUAL", "AUTO")
_VALID_SCOPES = ("all", "manual", "auto")


def _build_profile_response(profile) -> MemoryProfileResponse:
    sections, _ = parse_memory_profile(profile.content_md)
    return MemoryProfileResponse(
        content_md=profile.content_md,
        manual_sections=memory_sections_to_payload(sections["MANUAL"]),
        auto_sections=memory_sections_to_payload(sections["AUTO"]),
        created_at=profile.created_at or "",
        updated_at=profile.updated_at or profile.created_at or "",
        last_used_at=profile.last_used_at,
    )


def _validate_memory_type(memory_type: str) -> None:
    if memory_type not in _VALID_MEMORY_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="memory_type 无效",
        )


def _validate_memory_source(source: str) -> None:
    if source not in _VALID_MEMORY_SOURCES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="source 无效",
        )


def _validate_content(content: str) -> str:
    cleaned = content.strip()
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="content 不能为空",
        )
    return cleaned


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
    _validate_memory_type(body.memory_type)
    _validate_memory_source(body.source)
    content = _validate_content(body.content)

    profile = ensure_memory_profile(db, user.user_id)
    sections, _ = parse_memory_profile(profile.content_md)
    items = sections[body.source][body.memory_type]
    if content in items:
        return MemoryOperationResponse(message="该记忆已存在")

    items.append(content)
    _, changed = save_memory_profile_content(db, profile, render_memory_profile(sections))
    return MemoryOperationResponse(message="记忆已添加" if changed else "记忆无变化")


@router.put("/items", response_model=MemoryOperationResponse)
def update_memory_item(
    body: UpdateMemoryItemRequest,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    _validate_memory_type(body.memory_type)
    _validate_memory_source(body.source)
    old_content = _validate_content(body.old_content)
    new_content = _validate_content(body.new_content)

    profile = ensure_memory_profile(db, user.user_id)
    sections, _ = parse_memory_profile(profile.content_md)
    items = sections[body.source][body.memory_type]
    try:
        items.remove(old_content)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记忆不存在",
        )

    manual_items = sections["MANUAL"][body.memory_type]
    if new_content not in manual_items:
        manual_items.append(new_content)

    _, changed = save_memory_profile_content(db, profile, render_memory_profile(sections))
    return MemoryOperationResponse(message="记忆已更新" if changed else "记忆无变化")


@router.post("/items/promote", response_model=MemoryOperationResponse)
def promote_memory_item(
    body: PromoteMemoryItemRequest,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    _validate_memory_type(body.memory_type)
    content = _validate_content(body.content)

    profile = ensure_memory_profile(db, user.user_id)
    sections, _ = parse_memory_profile(profile.content_md)
    auto_items = sections["AUTO"][body.memory_type]
    try:
        auto_items.remove(content)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="自动记忆不存在",
        )

    manual_items = sections["MANUAL"][body.memory_type]
    if content not in manual_items:
        manual_items.append(content)

    _, changed = save_memory_profile_content(db, profile, render_memory_profile(sections))
    return MemoryOperationResponse(message="已提升为我的记忆" if changed else "记忆无变化")


@router.delete("")
def clear_memory_profile(
    scope: str = Query("all"),
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    if scope not in _VALID_SCOPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="scope 无效")

    profile = ensure_memory_profile(db, user.user_id)
    sections, _ = parse_memory_profile(profile.content_md)

    if scope == "all":
        new_content = render_memory_profile()
        message = "已清除全部记忆"
    elif scope == "manual":
        sections["MANUAL"] = {memory_type: [] for memory_type in _VALID_MEMORY_TYPES}
        new_content = render_memory_profile(sections)
        message = "已清除我的记忆"
    else:
        sections["AUTO"] = {memory_type: [] for memory_type in _VALID_MEMORY_TYPES}
        new_content = render_memory_profile(sections)
        message = "已清除自动记忆"

    save_memory_profile_content(db, profile, new_content)
    return {"message": message}


@router.delete("/items", response_model=MemoryOperationResponse)
def delete_memory_item(
    memory_type: str = Query(...),
    content: str = Query(...),
    source: str = Query("MANUAL"),
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    _validate_memory_type(memory_type)
    _validate_memory_source(source)

    profile = ensure_memory_profile(db, user.user_id)
    sections, _ = parse_memory_profile(profile.content_md)
    items = sections[source][memory_type]
    try:
        items.remove(content.strip())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记忆不存在",
        )

    _, changed = save_memory_profile_content(db, profile, render_memory_profile(sections))
    return MemoryOperationResponse(message="记忆已删除" if changed else "记忆无变化")
