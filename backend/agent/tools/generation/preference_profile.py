"""口令生成偏好：将用户设置映射为生成档位与默认参数。"""
from __future__ import annotations

from typing import Any

from agent.state import PassAgentState

_HIGH_SECURITY_KEYWORDS = (
    "银行", "支付", "财务", "工作", "公司", "邮箱", "admin", "root",
    "github", "gitlab", "服务器", "学校", "教务", "vpn", "wallet",
)
_MEMORABLE_KEYWORDS = (
    "好记", "容易记", "记住", "易记", "可读", "可念", "短语", "passphrase",
    "pronounceable", "好输入", "手动输入",
)


def _clamp_weight(weight: float) -> float:
    return min(max(weight, 0.1), 0.9)


def _last_user_text(state: PassAgentState) -> str:
    for msg in reversed(state.get("messages", [])):
        if hasattr(msg, "type") and getattr(msg, "type", None) == "human":
            return str(getattr(msg, "content", "") or "")
        if isinstance(msg, dict) and msg.get("role") == "user":
            return str(msg.get("content", "") or "")
    return ""


def _has_any_keyword(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = (text or "").lower()
    return any(keyword in lowered for keyword in keywords)


def resolve_generation_preference(
    state: PassAgentState,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """根据用户设置和当前请求，得到本次生成偏好档位。"""
    base_weight = _clamp_weight(float(state.get("gen_security_weight", 0.5) or 0.5))
    auto_mode = bool(state.get("gen_auto_mode", True))
    reasons: list[str] = []

    effective_weight = base_weight
    latest_text = _last_user_text(state)
    if auto_mode:
        if _has_any_keyword(latest_text, _HIGH_SECURITY_KEYWORDS):
            effective_weight = max(effective_weight, 0.7)
            reasons.append("high_sensitivity_context")
        if _has_any_keyword(latest_text, _MEMORABLE_KEYWORDS):
            effective_weight = min(effective_weight, 0.3)
            reasons.append("memorability_request")

    effective_weight = _clamp_weight(effective_weight)

    if effective_weight >= 0.85:
        profile = "highest_security"
        label = "最高安全"
    elif effective_weight >= 0.6:
        profile = "prefer_security"
        label = "偏安全"
    elif effective_weight >= 0.4:
        profile = "balanced"
        label = "均衡"
    elif effective_weight >= 0.2:
        profile = "prefer_memorability"
        label = "偏好记"
    else:
        profile = "most_memorable"
        label = "最好记"

    return {
        "auto_mode": auto_mode,
        "base_weight": round(base_weight, 2),
        "effective_weight": round(effective_weight, 2),
        "profile": profile,
        "label": label,
        "latest_text": latest_text,
        "reasons": reasons,
        "params": params or {},
    }


def default_random_constraints(pref: dict[str, Any]) -> dict[str, Any]:
    profile = pref["profile"]
    if profile == "highest_security":
        return {"min_length": 16, "max_length": 24, "count": 5, "require_upper": True, "require_digit": True, "require_special": True}
    if profile == "prefer_security":
        return {"min_length": 14, "max_length": 20, "count": 5, "require_upper": True, "require_digit": True, "require_special": True}
    if profile == "balanced":
        return {"min_length": 12, "max_length": 18, "count": 5, "require_upper": True, "require_digit": True, "require_special": True}
    if profile == "prefer_memorability":
        return {"min_length": 12, "max_length": 16, "count": 5, "require_upper": True, "require_digit": True, "require_special": True}
    return {"min_length": 10, "max_length": 14, "count": 5, "require_upper": True, "require_digit": True, "require_special": True}


def default_pronounceable_options(pref: dict[str, Any]) -> dict[str, Any]:
    profile = pref["profile"]
    if profile == "highest_security":
        return {"length": 16, "add_digit": True, "add_special": True}
    if profile == "prefer_security":
        return {"length": 14, "add_digit": True, "add_special": True}
    if profile == "balanced":
        return {"length": 12, "add_digit": True, "add_special": True}
    if profile == "prefer_memorability":
        return {"length": 10, "add_digit": True, "add_special": True}
    return {"length": 9, "add_digit": True, "add_special": False}


def default_passphrase_options(pref: dict[str, Any]) -> dict[str, Any]:
    profile = pref["profile"]
    if profile == "highest_security":
        return {"word_count": 6, "separator": "-", "capitalize": True, "add_number": True}
    if profile == "prefer_security":
        return {"word_count": 5, "separator": "-", "capitalize": True, "add_number": True}
    if profile == "balanced":
        return {"word_count": 4, "separator": "-", "capitalize": True, "add_number": True}
    if profile == "prefer_memorability":
        return {"word_count": 4, "separator": "-", "capitalize": False, "add_number": True}
    return {"word_count": 4, "separator": "-", "capitalize": False, "add_number": False}
