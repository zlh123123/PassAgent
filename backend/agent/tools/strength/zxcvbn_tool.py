"""zxcvbn_check 工具：评估口令熵值、评分、破解时间"""
from __future__ import annotations

from zxcvbn import zxcvbn

from agent.graph import register_tool
from agent.state import PassAgentState


def check_zxcvbn(password: str) -> dict:
    """调用 zxcvbn 评估口令强度。"""
    result = zxcvbn(password)

    crack_times = result["crack_times_display"]

    return {
        "score": result["score"],  # 0-4
        "guesses": float(result["guesses"]),
        "guesses_log10": round(float(result["guesses_log10"]), 2),
        "crack_times": {
            "online_throttled": crack_times["online_throttling_100_per_hour"],
            "online_unthrottled": crack_times["online_no_throttling_10_per_second"],
            "offline_slow": crack_times["offline_slow_hashing_1e4_per_second"],
            "offline_fast": crack_times["offline_fast_hashing_1e10_per_second"],
        },
        "feedback": {
            "warning": result["feedback"]["warning"],
            "suggestions": result["feedback"]["suggestions"],
        },
        "sequence_summary": [
            {
                "pattern": m["pattern"],
                "token": m["token"],
                "guesses_log10": round(m["guesses_log10"], 2),
            }
            for m in result["sequence"]
        ],
    }


@register_tool("zxcvbn_check")
async def zxcvbn_check_tool(state: PassAgentState) -> dict:
    """评估口令熵值、评分(0-4)、破解时间。"""
    params = state.get("action_params", {})
    password = params.get("password", "")

    result = check_zxcvbn(password)

    return {"_tool_result": result}
