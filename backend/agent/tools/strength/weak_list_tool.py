"""weak_list_match 工具：检查口令是否在弱口令库中"""
from __future__ import annotations

import os
from functools import lru_cache

from agent.graph import register_tool
from agent.state import PassAgentState

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "weak_passwords")


@lru_cache(maxsize=1)
def _load_lists() -> dict[str, set[str]]:
    """加载弱口令库到内存（仅首次调用时加载）。"""
    lists: dict[str, set[str]] = {}
    for name in ("top100", "top1000", "rockyou_sample"):
        path = os.path.join(_DATA_DIR, f"{name}.txt")
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lists[name] = {line.strip() for line in f if line.strip()}
        except FileNotFoundError:
            lists[name] = set()
    return lists


def check_weak_list(password: str) -> dict:
    """检查口令是否命中弱口令库。"""
    if not password:
        return {
            "in_top100": False,
            "in_top1000": False,
            "in_rockyou": False,
            "matched_list": None,
            "risk_level": "low",
        }

    lists = _load_lists()
    pw_lower = password.lower()

    in_top100 = password in lists.get("top100", set()) or pw_lower in lists.get("top100", set())
    in_top1000 = in_top100 or password in lists.get("top1000", set()) or pw_lower in lists.get("top1000", set())
    in_rockyou = in_top1000 or password in lists.get("rockyou_sample", set()) or pw_lower in lists.get("rockyou_sample", set())

    matched_list = None
    if in_top100:
        matched_list = "top100"
    elif in_top1000:
        matched_list = "top1000"
    elif in_rockyou:
        matched_list = "rockyou"

    risk = "high" if in_top1000 else "medium" if in_rockyou else "low"

    return {
        "in_top100": in_top100,
        "in_top1000": in_top1000,
        "in_rockyou": in_rockyou,
        "matched_list": matched_list,
        "risk_level": risk,
    }


@register_tool("weak_list_match")
async def weak_list_match_tool(state: PassAgentState) -> dict:
    """检查口令是否在弱口令库中（top100/top1000/rockyou）。"""
    params = state.get("action_params", {})
    password = params.get("password", "")
    return {"_tool_result": check_weak_list(password)}
