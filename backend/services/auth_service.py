"""注册、登录业务逻辑"""
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session as DBSession

from database.models import User
from utils.security import hash_password, verify_password, create_token
from services.email_service import verify_code


def register_user(
    db: DBSession,
    email: str,
    code: str,
    password: str,
    nickname: str | None,
) -> dict:
    """
    注册新用户。
    1. 校验验证码
    2. 检查邮箱是否已注册
    3. 创建用户并签发 JWT
    返回 {"user_id": ..., "token": ..., ...} 或抛出 ValueError。
    """
    # 验证码校验
    if not verify_code(email, code):
        raise ValueError("验证码错误或已过期")

    # 邮箱唯一性
    if db.query(User).filter(User.email == email).first():
        raise ValueError("该邮箱已注册")

    user_id = uuid.uuid4().hex
    now = datetime.now(timezone.utc).isoformat()

    user = User(
        user_id=user_id,
        email=email,
        password_hash=hash_password(password),
        nickname=nickname,
        theme="system",
        created_at=now,
    )
    db.add(user)
    db.commit()

    token = create_token(user_id)
    return {
        "user_id": user_id,
        "token": token,
        "nickname": nickname,
        "theme": "system",
        "font_size": "M",
        "bubble_style": "rounded",
        "gen_auto_mode": 1,
        "gen_security_weight": "0.5",
    }


def login_user(db: DBSession, email: str, password: str) -> dict:
    """
    登录。
    校验邮箱 + 密码，成功返回用户信息 + JWT，失败抛出 ValueError。
    """
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise ValueError("邮箱或密码错误")

    if not verify_password(password, user.password_hash):
        raise ValueError("邮箱或密码错误")

    token = create_token(user.user_id)
    return {
        "user_id": user.user_id,
        "token": token,
        "nickname": user.nickname,
        "theme": user.theme or "system",
        "font_size": user.font_size or "M",
        "bubble_style": user.bubble_style or "rounded",
        "gen_auto_mode": user.gen_auto_mode if user.gen_auto_mode is not None else 1,
        "gen_security_weight": user.gen_security_weight or "0.5",
    }
