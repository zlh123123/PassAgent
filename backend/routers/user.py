"""用户资料路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from database.connection import get_db
from database.models import User
from utils.deps import get_current_user
from utils.security import verify_password, hash_password
from schemas.user import ProfileResponse, UpdateProfileRequest, ChangePasswordRequest

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/profile", response_model=ProfileResponse)
def get_profile(user: User = Depends(get_current_user)):
    return ProfileResponse(
        user_id=user.user_id,
        email=user.email,
        nickname=user.nickname,
        theme=user.theme or "system",
        font_size=user.font_size or "M",
        bubble_style=user.bubble_style or "rounded",
        gen_auto_mode=user.gen_auto_mode if user.gen_auto_mode is not None else 1,
        gen_security_weight=user.gen_security_weight or "0.5",
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
        if body.theme not in ("light", "dark", "system"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="theme 只能是 light、dark 或 system",
            )
        user.theme = body.theme
    if body.font_size is not None:
        if body.font_size not in ("S", "M", "L", "XL"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="font_size 只能是 S、M、L 或 XL",
            )
        user.font_size = body.font_size
    if body.bubble_style is not None:
        if body.bubble_style not in ("rounded", "square", "minimal"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="bubble_style 只能是 rounded、square 或 minimal",
            )
        user.bubble_style = body.bubble_style
    if body.gen_auto_mode is not None:
        user.gen_auto_mode = body.gen_auto_mode
    if body.gen_security_weight is not None:
        user.gen_security_weight = body.gen_security_weight
    db.commit()
    return {"message": "更新成功"}


@router.put("/password")
def change_password(
    body: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    if not verify_password(body.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误",
        )
    user.password_hash = hash_password(body.new_password)
    db.commit()
    return {"message": "密码修改成功"}


@router.delete("/account")
def delete_account(
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    db.delete(user)
    db.commit()
    return {"message": "账户已删除"}
