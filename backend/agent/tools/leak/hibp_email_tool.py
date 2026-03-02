"""hibp_email_check 工具：通过 Hunter.io API 验证邮箱并获取关联信息

使用 Hunter.io Email Verification API 检查邮箱有效性，
使用 Combined Enrichment API 获取邮箱关联的个人和公司信息。
需要在 .env 中配置 HUNTER_API_KEY。
"""
from __future__ import annotations

import os

import httpx

from agent.graph import register_tool
from agent.state import PassAgentState

_HUNTER_BASE = "https://api.hunter.io/v2"
_HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "")
_TIMEOUT = 15


async def verify_email(email: str) -> dict:
    """验证邮箱有效性。"""
    if not _HUNTER_API_KEY:
        return {"error": "Hunter.io API Key 未配置，请在 .env 中添加 HUNTER_API_KEY"}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{_HUNTER_BASE}/email-verifier",
            params={"email": email, "api_key": _HUNTER_API_KEY},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})

    return {
        "email": data.get("email"),
        "result": data.get("result"),          # deliverable / undeliverable / risky / unknown
        "score": data.get("score"),            # 0-100
        "status": data.get("status"),          # valid / invalid / accept_all / webmail / disposable / unknown
        "disposable": data.get("disposable"),  # 是否一次性邮箱
        "webmail": data.get("webmail"),        # 是否 webmail（如 gmail）
        "mx_records": data.get("mx_records"),
        "smtp_server": data.get("smtp_server"),
        "smtp_check": data.get("smtp_check"),
        "block": data.get("block"),
    }


async def enrich_email(email: str) -> dict:
    """获取邮箱关联的个人和公司信息（Combined Enrichment）。"""
    if not _HUNTER_API_KEY:
        return {"error": "Hunter.io API Key 未配置，请在 .env 中添加 HUNTER_API_KEY"}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{_HUNTER_BASE}/combined/find",
            params={"email": email, "api_key": _HUNTER_API_KEY},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})

    person = data.get("person", {}) or {}
    company = data.get("company", {}) or {}

    result: dict = {
        "email": email,
    }

    # 个人信息
    if person:
        result["person"] = {
            "full_name": person.get("full_name"),
            "first_name": person.get("first_name"),
            "last_name": person.get("last_name"),
            "position": person.get("position"),
            "twitter": person.get("twitter"),
            "linkedin_url": person.get("linkedin_url"),
            "phone_number": person.get("phone_number"),
        }

    # 公司信息
    if company:
        result["company"] = {
            "name": company.get("name"),
            "domain": company.get("domain"),
            "industry": company.get("industry"),
            "country": company.get("country"),
            "state": company.get("state"),
            "city": company.get("city"),
        }

    return result


@register_tool("hibp_email_check")
async def hibp_email_check_tool(state: PassAgentState) -> dict:
    """查询邮箱有效性及关联信息。

    1. 先验证邮箱是否有效/可送达
    2. 再获取邮箱关联的个人和公司信息
    """
    params = state.get("action_params", {})
    email = params.get("email", "")

    if not email:
        return {"_tool_result": {"error": "未提供邮箱地址"}}

    results: dict = {"email": email}

    try:
        # 邮箱验证
        verification = await verify_email(email)
        results["verification"] = verification

        # 信息丰富（仅在验证无错误时执行）
        if "error" not in verification:
            enrichment = await enrich_email(email)
            results["enrichment"] = enrichment

    except httpx.HTTPStatusError as e:
        results["error"] = f"Hunter.io API 请求失败: {e.response.status_code}"
    except httpx.RequestError as e:
        results["error"] = f"网络请求失败: {str(e)}"

    return {"_tool_result": results}
