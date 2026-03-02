"""fetch_site_policy 工具：获取指定网站的密码策略要求

优先从本地 site_policies.json 查询，如果没有匹配则返回通用建议。
"""
from __future__ import annotations

import json
import os
from functools import lru_cache

from agent.graph import register_tool
from agent.state import PassAgentState

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")

# 通用密码策略（当网站不在库中时使用）
_DEFAULT_POLICY = {
    "site_name": "通用建议",
    "min_length": 8,
    "max_length": 128,
    "require_upper": True,
    "require_lower": True,
    "require_digit": True,
    "require_special": False,
    "allowed_specials": "!@#$%^&*()_+-=[]{}|;:,.<>?",
    "notes": "大多数网站要求至少 8 位，建议使用 12 位以上并包含多种字符类别。",
}

# 内置常见网站策略（补充 site_policies.json 为空时使用）
_BUILTIN_POLICIES: dict[str, dict] = {
    "github": {
        "site_name": "GitHub",
        "min_length": 8,
        "max_length": 128,
        "require_upper": False,
        "require_lower": False,
        "require_digit": False,
        "require_special": False,
        "allowed_specials": "all",
        "notes": "至少 8 位，或至少 15 位（可免除其他要求）。不能是常见弱密码。",
    },
    "google": {
        "site_name": "Google",
        "min_length": 8,
        "max_length": 100,
        "require_upper": False,
        "require_lower": False,
        "require_digit": False,
        "require_special": False,
        "allowed_specials": "all",
        "notes": "至少 8 个字符，可包含字母、数字和符号的任意组合。",
    },
    "apple": {
        "site_name": "Apple ID",
        "min_length": 8,
        "max_length": 128,
        "require_upper": True,
        "require_lower": True,
        "require_digit": True,
        "require_special": False,
        "allowed_specials": "all",
        "notes": "至少 8 位，需包含大写字母、小写字母和数字。",
    },
    "微信": {
        "site_name": "微信",
        "min_length": 8,
        "max_length": 16,
        "require_upper": False,
        "require_lower": True,
        "require_digit": True,
        "require_special": False,
        "allowed_specials": "_-",
        "notes": "8-16 位，需包含字母和数字的组合。",
    },
    "wechat": {
        "site_name": "微信",
        "min_length": 8,
        "max_length": 16,
        "require_upper": False,
        "require_lower": True,
        "require_digit": True,
        "require_special": False,
        "allowed_specials": "_-",
        "notes": "8-16 位，需包含字母和数字的组合。",
    },
    "steam": {
        "site_name": "Steam",
        "min_length": 7,
        "max_length": 64,
        "require_upper": True,
        "require_lower": True,
        "require_digit": False,
        "require_special": False,
        "allowed_specials": "all",
        "notes": "至少 7 位，需包含大写和小写字母。建议启用 Steam Guard 两步验证。",
    },
    "支付宝": {
        "site_name": "支付宝",
        "min_length": 8,
        "max_length": 20,
        "require_upper": False,
        "require_lower": True,
        "require_digit": True,
        "require_special": False,
        "allowed_specials": "!@#$%^&*()_+-=",
        "notes": "8-20 位，需包含字母和数字。",
    },
    "alipay": {
        "site_name": "支付宝",
        "min_length": 8,
        "max_length": 20,
        "require_upper": False,
        "require_lower": True,
        "require_digit": True,
        "require_special": False,
        "allowed_specials": "!@#$%^&*()_+-=",
        "notes": "8-20 位，需包含字母和数字。",
    },
    "淘宝": {
        "site_name": "淘宝",
        "min_length": 6,
        "max_length": 20,
        "require_upper": False,
        "require_lower": False,
        "require_digit": False,
        "require_special": False,
        "allowed_specials": "!@#$%^&*()_+-=",
        "notes": "6-20 位，建议使用字母+数字组合。",
    },
    "bilibili": {
        "site_name": "Bilibili",
        "min_length": 6,
        "max_length": 20,
        "require_upper": False,
        "require_lower": False,
        "require_digit": False,
        "require_special": False,
        "allowed_specials": "!@#$%^&*()_+-=",
        "notes": "6-20 位，至少包含两种字符类型。",
    },
    "twitter": {
        "site_name": "Twitter/X",
        "min_length": 8,
        "max_length": 128,
        "require_upper": False,
        "require_lower": False,
        "require_digit": False,
        "require_special": False,
        "allowed_specials": "all",
        "notes": "至少 8 位。",
    },
    "x": {
        "site_name": "Twitter/X",
        "min_length": 8,
        "max_length": 128,
        "require_upper": False,
        "require_lower": False,
        "require_digit": False,
        "require_special": False,
        "allowed_specials": "all",
        "notes": "至少 8 位。",
    },
}


@lru_cache(maxsize=1)
def _load_policies() -> dict[str, dict]:
    """加载本地策略文件，合并内置策略。"""
    policies = dict(_BUILTIN_POLICIES)

    path = os.path.join(_DATA_DIR, "site_policies.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            # 文件格式：{ "site_key": { policy_fields... }, ... }
            for key, policy in data.items():
                policies[key.lower()] = policy
        elif isinstance(data, list):
            for item in data:
                name = item.get("site_name", "").lower()
                if name:
                    policies[name] = item
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    return policies


def fetch_policy(site_name: str) -> dict:
    """查询网站密码策略。"""
    policies = _load_policies()
    key = site_name.lower().strip()

    # 精确匹配
    if key in policies:
        return {"found": True, "policy": policies[key]}

    # 模糊匹配
    for pk, pv in policies.items():
        if key in pk or pk in key:
            return {"found": True, "policy": pv}
        site_display = pv.get("site_name", "").lower()
        if key in site_display or site_display in key:
            return {"found": True, "policy": pv}

    return {"found": False, "policy": _DEFAULT_POLICY}


@register_tool("fetch_site_policy")
async def site_policy_tool(state: PassAgentState) -> dict:
    """获取指定网站的密码策略要求。"""
    params = state.get("action_params", {})
    site_name = params.get("site_name", "")
    return {"_tool_result": fetch_policy(site_name)}
