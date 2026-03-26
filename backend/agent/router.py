"""Intent Router 节点：轻量级意图分类 + TODO List 生成

不使用 Function Calling，纯 JSON 输出。
将用户请求分类到对应的 skill，并生成执行计划。
"""
from __future__ import annotations

import json
import logging
from openai import AsyncOpenAI

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from agent.state import PassAgentState
from agent.skills import SKILL_REGISTRY, VALID_SKILLS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Router System Prompt（精简，不含任何工具定义）
# ---------------------------------------------------------------------------
ROUTER_SYSTEM_PROMPT = """\
你是 PassAgent 的意图路由器。根据用户消息，完成两件事：
1. 将用户意图分类到一个 skill
2. 生成一个 TODO List（执行计划）

## Skill 分类

- **strength-assessment**: 用户想检测/评估口令强度（如"帮我看看这个密码安全吗"）
- **password-generation**: 用户想生成新的安全口令（如"帮我生成一个密码"）
- **breach-checking**: 用户想查询密码或邮箱是否泄露（如"这个密码有没有被泄露"）
- **password-recovery**: 用户想恢复/找回忘记的口令（如"我忘了密码，只记得一些片段"）
- **graphical-mode**: 用户想使用图形口令或解读 PassInfinity 体验结果（如"我想用图片设密码"、"帮我看看刚保存的 PassInfinity 方案"）
- **off_topic**: 与口令安全无关的闲聊或问候，或恶意破解请求
- **multi_skill**: 请求涉及多个技能（如"生成一个密码并检测强度"）

## TODO List 规则

- 每个步骤包含：step_id（序号）、description（描述）、tool_name（预计工具，可为 null）
- multi_skill 时，每个步骤额外标注 skill 字段
- 涉及口令生成或恢复时，第一步应为 retrieve_memory（检索用户记忆）
- 最后一步通常是 respond（汇总回复）
- off_topic 时 todo_list 为空数组

## 输出格式

严格输出 JSON，不要有任何额外文字：

```json
{
  "skill": "strength-assessment",
  "todo_list": [
    {"step_id": 1, "description": "用 zxcvbn 评估熵值", "tool_name": "zxcvbn_check"},
    {"step_id": 2, "description": "分析字符组成", "tool_name": "basic_analysis"},
    {"step_id": 3, "description": "检测键盘/日期模式", "tool_name": "pattern_detect"},
    {"step_id": 4, "description": "汇总结果回复用户", "tool_name": "respond"}
  ]
}
```"""

# ---------------------------------------------------------------------------
# Router 角色 → OpenAI 消息映射
# ---------------------------------------------------------------------------
TYPE_ROLE_MAP = {
    "human": "user",
    "ai": "assistant",
    "system": "system",
    "tool": "tool",
}

_GRAPHICAL_KEYWORDS = (
    "passinfinity",
    "图片密码",
    "图片选点",
    "图片记忆点",
    "图形口令",
    "图像因子",
    "地图密码",
    "位置密码",
    "地理位置因子",
    "地图位置因子",
    "富文本标记",
    "文本标记",
    "样式标记",
)
_MFA_HINTS = ("多因子认证", "多因素认证", "mfa")
_CLASSIC_MFA_HINTS = (
    "otp",
    "totp",
    "2fa",
    "验证码",
    "短信",
    "谷歌验证",
    "google authenticator",
    "microsoft authenticator",
    "邮箱验证码",
    "动态码",
)
_EXPERIENCE_HINTS = ("玩", "体验", "试试", "试一下", "打开", "进入")
_ARTIFACT_READ_HINTS = (
    "解释",
    "解读",
    "分析",
    "看看",
    "读取",
    "刚保存",
    "保存的",
    "最近保存",
    "方案",
)
_OPEN_PAGE_HINTS = ("开链接", "打开链接", "链接", "开页面", "打开页面", "跳转", "进入页面", "去看看")

_MODE_KEYWORDS = {
    "image": ("图片记忆点", "图片密码", "图片选点", "图片因子", "图像因子", "图片"),
    "map": ("地图位置因子", "地图密码", "位置密码", "地理位置因子", "地图", "位置"),
    "richtext": ("富文本标记", "文本标记", "样式标记", "富文本"),
}

_GRAPHICAL_RESPONSE_HINT = (
    "当前用户是在了解 PassInfinity，但还没有明确选择图片记忆点、地图位置因子或富文本标记。"
    "请不要让用户立即跳转页面。"
    "请用很简洁的中文介绍这三种模式各自是做什么的，并在结尾直接问用户想先体验哪一种。"
    "不要展开泛泛的 MFA 科普，不要输出技术大段落。"
)


def _get_latest_user_message_text(state: PassAgentState) -> str:
    for msg in reversed(state["messages"]):
        msg_type = getattr(msg, "type", None)
        role = msg.get("role") if isinstance(msg, dict) else None
        if msg_type == "human" or role == "user":
            content = msg.content if hasattr(msg, "content") else msg.get("content", "")
            return str(content or "").strip()
    return ""


def _get_recent_message_texts(state: PassAgentState, limit: int = 6) -> list[str]:
    recent = state["messages"][-limit:]
    texts: list[str] = []
    for msg in recent:
        content = msg.content if hasattr(msg, "content") else msg.get("content", "")
        text = str(content or "").strip()
        if text:
            texts.append(text)
    return texts


def _detect_mode(text: str) -> str | None:
    lowered = text.lower()
    for mode, keywords in _MODE_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return mode
    return None


def _build_todo(skill: str, items: list[tuple[str, str | None]]) -> list[dict]:
    todo_list = []
    for index, (description, tool_name) in enumerate(items, start=1):
        todo_list.append({
            "step_id": index,
            "description": description,
            "tool_name": tool_name,
            "skill": skill,
            "status": "pending",
            "result_summary": "",
        })
    return todo_list


def _match_graphical_mode(state: PassAgentState) -> tuple[str, list[dict]] | None:
    latest_text = _get_latest_user_message_text(state)
    text = latest_text.lower()
    if not text:
        return None

    recent_texts = [item.lower() for item in _get_recent_message_texts(state)]
    recent_context = "\n".join(recent_texts)

    mentions_graphical = any(keyword in text for keyword in _GRAPHICAL_KEYWORDS)
    mentions_mfa = any(keyword in text for keyword in _MFA_HINTS)
    mentions_classic_mfa = any(keyword in text for keyword in _CLASSIC_MFA_HINTS)
    mentions_experience = any(keyword in text for keyword in _EXPERIENCE_HINTS)
    mentions_open_page = any(keyword in text for keyword in _OPEN_PAGE_HINTS)
    recent_graphical = any(keyword in recent_context for keyword in _GRAPHICAL_KEYWORDS)

    if (
        not mentions_graphical
        and not (mentions_mfa and not mentions_classic_mfa and mentions_experience)
        and not recent_graphical
    ):
        return None

    wants_artifact = "passinfinity" in text and any(keyword in text for keyword in _ARTIFACT_READ_HINTS)
    if wants_artifact:
        return (
            "graphical-mode",
            _build_todo(
                "graphical-mode",
                [
                    ("读取最近保存的 PassInfinity 结果", "passinfinity_artifact"),
                    ("解读结果并给出建议", "respond"),
                ],
            ),
        )

    mode = _detect_mode(text)
    if mode is None and mentions_open_page:
        mode = _detect_mode(recent_context)

    if mode is None and (mentions_graphical or mentions_mfa):
        mode = "select"

    description_map = {
        "select": "介绍 PassInfinity 的三种模式并询问用户选择",
        "image": "打开 PassInfinity 页面（图片模式）",
        "map": "打开 PassInfinity 页面（地图模式）",
        "richtext": "打开 PassInfinity 页面（富文本模式）",
    }
    if mode is None:
        return None

    tool_name = None if mode == "select" else "graphical_mode"
    return (
        "graphical-mode",
        _build_todo(
            "graphical-mode",
            [
                (description_map[mode], tool_name),
                ("说明如何使用 PassInfinity 页面", "respond") if mode != "select" else ("等待用户选择具体模式", "respond"),
            ],
        ),
    )


def _build_router_messages(state: PassAgentState) -> list[dict]:
    """构建 router 的 messages 列表。"""
    system_content = ROUTER_SYSTEM_PROMPT

    # 附加上下文信息（精简）
    context_parts: list[str] = []

    if state.get("uploaded_files"):
        context_parts.append(
            f"用户上传了文件: {json.dumps(state['uploaded_files'], ensure_ascii=False)}"
        )

    gen_auto = state.get("gen_auto_mode", True)
    gen_weight = state.get("gen_security_weight", 0.5)
    if not gen_auto:
        context_parts.append(f"生成偏好: 手动模式（安全性权重 α={gen_weight}）")

    if state.get("memories"):
        context_parts.append(f"已有用户记忆 {len(state['memories'])} 条")

    if context_parts:
        system_content += "\n\n[当前状态]\n" + "\n".join(context_parts)

    messages: list[dict] = [{"role": "system", "content": system_content}]

    # 追加对话历史
    for msg in state["messages"]:
        if hasattr(msg, "type"):
            role = TYPE_ROLE_MAP.get(msg.type, "user")
        else:
            role = msg.get("role", "user")

        content = msg.content if hasattr(msg, "content") else msg.get("content", "")
        if not content or role == "system":
            continue
        messages.append({"role": role, "content": content})

    return messages


def _parse_router_response(text: str) -> dict | None:
    """从 LLM 文本响应中解析 JSON。支持 ```json 包裹和裸 JSON。"""
    text = text.strip()

    # 去掉 markdown 代码块包裹
    if text.startswith("```"):
        lines = text.split("\n")
        # 去掉首行 ```json 和末尾 ```
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 尝试找到第一个 { 到最后一个 } 之间的内容
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
    return None


async def intent_router_node(state: PassAgentState) -> dict:
    """Intent Router 节点：分类意图 + 生成 TODO List。

    返回对 state 的 partial update：
    - active_skill: skill 名称
    - todo_list: 执行计划
    - next_action: off_topic 时为 "respond"，否则为 None
    """
    client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    event_queue = state.get("_event_queue")
    latest_text = _get_latest_user_message_text(state)

    graphical_match = _match_graphical_mode(state)
    if graphical_match is not None:
        skill, todo_list = graphical_match
        next_action = None
        response_hint = None
        first_tool_name = todo_list[0].get("tool_name") if todo_list else None
        if first_tool_name is None:
            next_action = "respond"
            response_hint = _GRAPHICAL_RESPONSE_HINT
        if event_queue is not None:
            await event_queue.put({
                "event": "agent_step",
                "data": {
                    "node": "intent_router",
                    "action": skill,
                    "reasoning": f"命中图形口令规则：{latest_text}",
                    "todo_list": todo_list,
                },
            })
        logger.info("Router heuristic matched graphical-mode, todo_steps=%d", len(todo_list))
        return {
            "active_skill": skill,
            "todo_list": todo_list,
            "current_step_index": 0,
            "next_action": next_action,
            "action_params": {},
            "response_hint": response_hint,
        }

    messages = _build_router_messages(state)
    logger.info("Router request: model=%s, message_count=%d", LLM_MODEL, len(messages))

    try:
        create_kwargs = dict(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=1024,
        )
        # 本地模型的特殊参数
        if LLM_MODEL != "deepseek-chat":
            create_kwargs["extra_body"] = {
                "repetition_penalty": 1.05,
                "chat_template_kwargs": {"enable_thinking": False},
            }

        response = await client.chat.completions.create(**create_kwargs)
    except Exception as e:
        logger.error("Router LLM call failed: %s", e)
        # 降级：直接走 respond
        return {
            "active_skill": "off_topic",
            "todo_list": [],
            "next_action": "respond",
            "action_params": {"reasoning": f"Router LLM 调用失败: {e}"},
            "loop_count": state.get("loop_count", 0) + 1,
        }
    finally:
        await client.close()

    raw_text = response.choices[0].message.content or ""
    logger.info("Router raw response: %s", raw_text[:500])

    parsed = _parse_router_response(raw_text)

    if parsed is None:
        logger.warning("Router failed to parse JSON, fallback to off_topic")
        return {
            "active_skill": "off_topic",
            "todo_list": [],
            "next_action": "respond",
            "action_params": {"reasoning": "Router 无法解析意图，降级为闲聊回复"},
            "loop_count": state.get("loop_count", 0) + 1,
        }

    skill = parsed.get("skill", "off_topic")
    if skill not in VALID_SKILLS:
        logger.warning("Router returned invalid skill: %s, fallback to off_topic", skill)
        skill = "off_topic"

    raw_todo = parsed.get("todo_list", [])

    # 规范化 todo_list
    todo_list = []
    for item in raw_todo:
        todo_list.append({
            "step_id": item.get("step_id", len(todo_list) + 1),
            "description": item.get("description", ""),
            "tool_name": item.get("tool_name"),
            "skill": item.get("skill", skill if skill != "multi_skill" else None),
            "status": "pending",
            "result_summary": "",
        })

    # 推送 SSE 事件
    if event_queue is not None:
        await event_queue.put({
            "event": "agent_step",
            "data": {
                "node": "intent_router",
                "action": skill,
                "reasoning": f"识别意图: {skill}，计划 {len(todo_list)} 步",
                "todo_list": todo_list,
            },
        })

    logger.info("Router result: skill=%s, todo_steps=%d", skill, len(todo_list))

    # off_topic 直接走 respond
    if skill == "off_topic":
        return {
            "active_skill": skill,
            "todo_list": [],
            "next_action": "respond",
            "action_params": {"reasoning": "用户请求与口令安全无关，直接回复"},
            "loop_count": state.get("loop_count", 0) + 1,
        }

    return {
        "active_skill": skill,
        "todo_list": todo_list,
        "current_step_index": 0,
        "next_action": None,
        "action_params": {},
    }
