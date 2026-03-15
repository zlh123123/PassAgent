"""bcrypt 密码哈希、JWT 编解码、密码强度校验"""
import re
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_HOURS


# 密码强度校验

def validate_password_strength(password: str) -> str | None:
    """
    校验密码强度，通过返回 None，不通过返回错误提示。
    要求：至少8位，包含大写字母、小写字母和数字。
    """
    if len(password) < 8:
        return "密码长度至少8位"
    if not re.search(r"[A-Z]", password):
        return "密码必须包含至少一个大写字母"
    if not re.search(r"[a-z]", password):
        return "密码必须包含至少一个小写字母"
    if not re.search(r"\d", password):
        return "密码必须包含至少一个数字"
    return None


# 密码哈希

def hash_password(plain: str) -> str:
    """明文 -> bcrypt 哈希"""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """校验明文与哈希是否匹配"""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# JWT

def create_token(user_id: str) -> str:
    """签发 JWT，payload 包含 user_id 和过期时间"""
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    """解码 JWT，失败返回 None"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
