"""breach_detail 工具：查询 HIBP 泄露事件信息

提供两个能力：
1. 列出全部已知泄露事件（GET /api/v3/breaches）
2. 查询单个泄露事件详情（GET /api/v3/breach/{name}）

两个端点均为公开 API，无需 API Key。
"""
from __future__ import annotations

import httpx

from agent.graph import register_tool
from agent.state import PassAgentState

_HIBP_BASE = "https://haveibeenpwned.com/api/v3"
_USER_AGENT = "PassAgent/1.0"
_TIMEOUT = 15


async def list_breaches(domain: str | None = None) -> dict:
    """获取全部泄露事件列表（可按域名筛选）。"""
    params = {}
    if domain:
        params["domain"] = domain

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{_HIBP_BASE}/breaches",
            params=params,
            headers={"User-Agent": _USER_AGENT},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

    # 精简返回（全量列表字段过多），只保留关键信息
    breaches = []
    for b in data:
        breaches.append({
            "name": b.get("Name"),
            "title": b.get("Title"),
            "domain": b.get("Domain"),
            "breach_date": b.get("BreachDate"),
            "pwn_count": b.get("PwnCount"),
            "data_classes": b.get("DataClasses", []),
            "is_verified": b.get("IsVerified"),
        })

    return {
        "total": len(breaches),
        "breaches": breaches,
    }


async def get_breach_detail(breach_name: str) -> dict:
    """获取单个泄露事件的详细信息。"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{_HIBP_BASE}/breach/{breach_name}",
            headers={"User-Agent": _USER_AGENT},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

    return {
        "name": data.get("Name"),
        "title": data.get("Title"),
        "domain": data.get("Domain"),
        "breach_date": data.get("BreachDate"),
        "added_date": data.get("AddedDate"),
        "modified_date": data.get("ModifiedDate"),
        "pwn_count": data.get("PwnCount"),
        "description": data.get("Description"),
        "logo_path": data.get("LogoPath"),
        "data_classes": data.get("DataClasses", []),
        "is_verified": data.get("IsVerified"),
        "is_fabricated": data.get("IsFabricated"),
        "is_sensitive": data.get("IsSensitive"),
        "is_retired": data.get("IsRetired"),
        "is_spam_list": data.get("IsSpamList"),
    }


@register_tool("breach_detail")
async def breach_detail_tool(state: PassAgentState) -> dict:
    """获取泄露事件信息。

    参数中有 breach_name 时查询单个事件详情，否则列出全部事件。
    """
    params = state.get("action_params", {})
    breach_name = params.get("breach_name", "")

    try:
        if breach_name:
            result = await get_breach_detail(breach_name)
        else:
            domain = params.get("domain")
            result = await list_breaches(domain)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            result = {"error": f"未找到泄露事件: {breach_name}"}
        else:
            result = {"error": f"HIBP API 请求失败: {e.response.status_code}"}
    except httpx.RequestError as e:
        result = {"error": f"网络请求失败: {str(e)}"}

    return {"_tool_result": result}
