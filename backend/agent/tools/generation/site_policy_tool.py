"""fetch_site_policy 工具：获取指定网站的密码策略要求

优先从本地 site_policies.json（Apple password-manager-resources 格式）查询，
再查内置策略，最后返回通用建议。
"""
from __future__ import annotations

import json
import os
import re
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

# 内置常见网站策略（补充 site_policies.json 中没有的中文站点等）
_BUILTIN_POLICIES: dict[str, dict] = {
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
}


def _parse_password_rules(domain: str, rules_str: str) -> dict:
    """将 Apple password-rules 格式解析为结构化策略字典。

    例如: "minlength: 8; maxlength: 20; required: lower; required: upper; required: digit;"
    """
    policy: dict = {
        "site_name": domain,
        "min_length": 8,
        "max_length": 128,
        "require_upper": False,
        "require_lower": False,
        "require_digit": False,
        "require_special": False,
        "allowed_specials": "all",
        "notes": "",
    }

    parts = [p.strip().rstrip(";") for p in rules_str.split(";") if p.strip()]
    special_chars_collected: list[str] = []
    notes_parts: list[str] = []

    for part in parts:
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        key = key.strip().lower()
        value = value.strip()

        if key == "minlength":
            policy["min_length"] = int(value)
        elif key == "maxlength":
            policy["max_length"] = int(value)
        elif key == "max-consecutive":
            notes_parts.append(f"相同字符最多连续 {value} 次")
        elif key == "required":
            # value 可以是 "lower", "upper", "digit", "special",
            # "[!@#$%]", 或组合如 "lower, upper" / "upper,lower,[#$]"
            tokens = re.split(r",\s*", value)
            for token in tokens:
                token = token.strip()
                t = token.lower()
                if t == "lower":
                    policy["require_lower"] = True
                elif t == "upper":
                    policy["require_upper"] = True
                elif t == "digit":
                    policy["require_digit"] = True
                elif t == "special":
                    policy["require_special"] = True
                elif t.startswith("[") and t.endswith("]"):
                    policy["require_special"] = True
                    chars = t[1:-1]
                    special_chars_collected.append(chars)
                elif t == "ascii-printable":
                    pass  # 允许所有可打印 ASCII
        elif key == "allowed":
            tokens = re.split(r",\s*", value)
            for token in tokens:
                token = token.strip()
                t = token.lower()
                if t.startswith("[") and t.endswith("]"):
                    chars = t[1:-1]
                    special_chars_collected.append(chars)

    if special_chars_collected:
        policy["allowed_specials"] = "".join(special_chars_collected)

    if notes_parts:
        policy["notes"] = "；".join(notes_parts) + "。"

    return policy


@lru_cache(maxsize=1)
def _load_policies() -> dict[str, dict]:
    """加载 Apple password-manager-resources 格式的策略文件，合并内置策略。"""
    policies: dict[str, dict] = {}

    # 1. 加载 site_policies.json（Apple password-rules 格式）
    path = os.path.join(_DATA_DIR, "site_policies.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data: dict = json.load(f)
        for domain, entry in data.items():
            rules_str = entry.get("password-rules", "")
            if rules_str:
                parsed = _parse_password_rules(domain, rules_str)
                policies[domain.lower()] = parsed
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # 2. 内置策略（不覆盖已有的）
    for key, policy in _BUILTIN_POLICIES.items():
        if key.lower() not in policies:
            policies[key.lower()] = policy

    return policies


def _extract_domain_parts(domain: str) -> tuple[str, str]:
    """从域名提取主体和完整基础域名。

    例如: "account.samsung.com" -> ("samsung", "samsung.com")
          "amazon.com" -> ("amazon", "amazon.com")
          "淘宝" -> ("淘宝", "淘宝")
    """
    parts = domain.split(".")
    if len(parts) >= 2:
        # 取倒数第二段作为主体名（跳过 .com / .co.jp 等后缀）
        tld_like = {"com", "net", "org", "edu", "gov", "co", "ac", "io"}
        if len(parts) >= 3 and parts[-2] in tld_like:
            return parts[-3], ".".join(parts[-3:])
        return parts[-2], ".".join(parts[-2:])
    return domain, domain


def fetch_policy(site_name: str) -> dict:
    """查询网站密码策略，按匹配质量分层查找。"""
    policies = _load_policies()
    key = site_name.lower().strip()

    if not key:
        return {"found": False, "policy": _DEFAULT_POLICY}

    # --- 第 1 层：精确匹配 ---
    if key in policies:
        return {"found": True, "policy": policies[key]}

    # --- 第 2 层：域名主体精确匹配 ---
    # 用户输入 "amazon" 精确匹配 "amazon.com" 的主体 "amazon"
    for pk, pv in policies.items():
        base_name, _ = _extract_domain_parts(pk)
        if key == base_name:
            return {"found": True, "policy": pv}

    # --- 第 3 层：用户输入是子域或完整域，匹配基础域名 ---
    # 用户输入 "account.samsung.com" 匹配 "account.samsung.com" 或 "samsung.com"
    _, key_base_domain = _extract_domain_parts(key)
    for pk, pv in policies.items():
        _, pk_base_domain = _extract_domain_parts(pk)
        if key_base_domain == pk_base_domain:
            return {"found": True, "policy": pv}

    # --- 第 4 层：site_name 显示名精确匹配 ---
    for pk, pv in policies.items():
        site_display = pv.get("site_name", "").lower()
        if key == site_display:
            return {"found": True, "policy": pv}

    # --- 第 5 层：域名主体前缀/包含匹配（需要 key 长度 >= 3 防止过于宽泛） ---
    if len(key) >= 3:
        candidates: list[tuple[str, dict]] = []
        for pk, pv in policies.items():
            base_name, _ = _extract_domain_parts(pk)
            # 域名主体以用户输入开头，或用户输入以域名主体开头
            if base_name.startswith(key) or key.startswith(base_name):
                candidates.append((pk, pv))
        # 选最短的域名（最可能是用户想要的主站）
        if candidates:
            best = min(candidates, key=lambda x: len(x[0]))
            return {"found": True, "policy": best[1]}

    return {"found": False, "policy": _DEFAULT_POLICY}


@register_tool("fetch_site_policy")
async def site_policy_tool(state: PassAgentState) -> dict:
    """获取指定网站的密码策略要求。"""
    params = state.get("action_params", {})
    site_name = params.get("site_name", "")
    return {"_tool_result": fetch_policy(site_name)}
