"""认证路由：发送验证码 / 注册 / 登录"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from database.connection import get_db
from schemas.auth import (
    SendCodeRequest,
    SendCodeResponse,
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
)
from services.email_service import store_code, send_code_email
from services.auth_service import register_user, login_user
from config import VERIFY_CODE_EXPIRE_SECONDS

router = APIRouter(prefix="/api/auth", tags=["auth"])


# POST /api/auth/send-code
@router.post("/send-code", response_model=SendCodeResponse)
async def send_code(body: SendCodeRequest):
    """发送邮箱验证码"""
    code = store_code(body.email)
    ok = await send_code_email(body.email, code)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="验证码发送失败，请稍后重试",
        )
    return SendCodeResponse(
        message="验证码已发送",
        expires_in=VERIFY_CODE_EXPIRE_SECONDS,
    )


# POST /api/auth/register
@router.post("/register", response_model=RegisterResponse)
def register(body: RegisterRequest, db: DBSession = Depends(get_db)):
    """注册新用户"""
    try:
        result = register_user(
            db,
            email=body.email,
            code=body.code,
            password=body.password,
            nickname=body.nickname,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return RegisterResponse(**result)


# POST /api/auth/login
@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: DBSession = Depends(get_db)):
    """登录"""
    try:
        result = login_user(db, email=body.email, password=body.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    return LoginResponse(**result)
