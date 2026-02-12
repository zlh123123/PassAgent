"""用户资料路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from database.connection import get_db
from database.models import User
from utils.deps import get_current_user
from schemas.user import ProfileResponse, UpdateProfileRequest

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/profile", response_model=ProfileResponse)
def get_profile(user: User = Depends(get_current_user)):
    return ProfileResponse(
        user_id=user.user_id,
        email=user.email,
        nickname=user.nickname,
        theme=user.theme or "light",
    )


@router.put("/profile")
def update_profile(
    body: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    if body.nickname is not None:
        user.nickname = body.nickname
    if body.theme is not None:
        if body.theme not in ("light", "dark"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="theme 只能是 light 或 dark",
            )
        user.theme = body.theme
    db.commit()
    return {"message": "更新成功"}
