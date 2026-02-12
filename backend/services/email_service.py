"""发送验证码邮件（Resend）"""
import random
import time
from typing import Dict, Tuple

import httpx

from config import RESEND_API_KEY, EMAIL_FROM, VERIFY_CODE_EXPIRE_SECONDS

# 内存缓存：email -> (code, expire_timestamp)
_code_store: Dict[str, Tuple[str, float]] = {}


def generate_code() -> str:
    """生成 6 位数字验证码"""
    return f"{random.randint(0, 999999):06d}"


def store_code(email: str) -> str:
    """生成并缓存验证码，返回验证码字符串"""
    code = generate_code()
    _code_store[email] = (code, time.time() + VERIFY_CODE_EXPIRE_SECONDS)
    return code


def verify_code(email: str, code: str) -> bool:
    """校验验证码是否正确且未过期，校验后立即删除"""
    stored = _code_store.get(email)
    if stored is None:
        return False
    stored_code, expire_at = stored
    if time.time() > expire_at:
        _code_store.pop(email, None)
        return False
    if stored_code != code:
        return False
    _code_store.pop(email, None)
    return True


async def send_code_email(email: str, code: str) -> bool:
    """通过 Resend API 发送验证码邮件，返回是否成功"""
    # 没配置 API Key 时走 dev 模式，直接打印到控制台
    if not RESEND_API_KEY:
        print(f"[DEV] 验证码 -> {email}: {code}")
        return True

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json={
                "from": EMAIL_FROM,
                "to": [email],
                "subject": "PassAgent 验证码",
                "html": (
                    f"<p>你的验证码是：<strong>{code}</strong></p>"
                    f"<p>{VERIFY_CODE_EXPIRE_SECONDS // 60} 分钟内有效。</p>"
                ),
            },
        )
        return resp.status_code == 200
