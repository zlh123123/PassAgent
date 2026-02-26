"""hibp_password_check 工具：通过 k-Anonymity 查询密码是否在泄露数据库中"""
from __future__ import annotations

import hashlib

import httpx

from agent.graph import register_tool
from agent.state import PassAgentState

# HIBP Pwned Passwords API（k-Anonymity，无需 API Key）
_HIBP_RANGE_URL = "https://api.pwnedpasswords.com/range/{prefix}"
_TIMEOUT = 10  # 秒


async def check_hibp_password(password: str) -> dict:
    """通过 HIBP k-Anonymity API 查询密码是否出现在泄露数据库中。

    原理：
    1. 对密码做 SHA-1 哈希并转为大写十六进制
    2. 取前 5 位作为 prefix 发送给 HIBP API
    3. API 返回所有匹配该前缀的 suffix:count 列表
    4. 在本地比对 suffix，避免明文密码或完整哈希泄露给第三方
    """
    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]

    async with httpx.AsyncClient() as client:
        response = await client.get(
            _HIBP_RANGE_URL.format(prefix=prefix),
            headers={"User-Agent": "PassAgent-LeakCheck"},
            timeout=_TIMEOUT,
        )
        response.raise_for_status()

    # 解析响应：每行格式为 "SUFFIX:COUNT"
    leaked = False
    count = 0
    for line in response.text.splitlines():
        parts = line.split(":")
        if len(parts) == 2 and parts[0] == suffix:
            leaked = True
            count = int(parts[1])
            break

    return {
        "leaked": leaked,
        "count": count,
    }


@register_tool("hibp_password_check")
async def hibp_password_check_tool(state: PassAgentState) -> dict:
    """通过 k-Anonymity 查询密码是否在泄露数据库中。"""
    params = state.get("action_params", {})
    password = params.get("password", "")

    try:
        result = await check_hibp_password(password)
    except httpx.HTTPStatusError as e:
        result = {"leaked": False, "count": 0, "error": f"HIBP API 请求失败: {e.response.status_code}"}
    except httpx.RequestError as e:
        result = {"leaked": False, "count": 0, "error": f"网络请求失败: {str(e)}"}

    return {"_tool_result": result}
