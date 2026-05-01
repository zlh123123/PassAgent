"""记忆写入：维护单份 markdown 记忆档案。"""
from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI
from sqlalchemy.orm import Session as DBSession

from agent.memory.profile import (
    ensure_memory_profile,
    normalize_memory_sections,
    parse_memory_profile,
    render_memory_profile,
    save_memory_profile_content,
)
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

logger = logging.getLogger(__name__)

EXTRACT_PROMPT = """\
你是 PassAgent 的记忆整理器。你只负责维护用户记忆文档中的「Agent 自动提炼」区域。

## 记忆类型
- preferences: 用户稳定偏好
- facts: 用户长期事实
- constraints: 明确约束

## 总目标
1. 只保留稳定、长期有用、对口令生成/恢复/风险分析/PassInfinity 有帮助的信息
2. 记忆必须简短，避免冗长解释
3. 每条尽量是一句短句
4. 每个 section 最多 8 条
5. 不要记录临时指令、一次性任务、寒暄、文件全文
6. 绝不存储明文密码、密码片段、哈希、验证码
7. 用户手动添加区域绝不能修改，也不要复制成自动记忆
8. 如果本轮对话没有值得写入的新长期信息，或自动记忆区无需变化，就不要更新
9. 输出 should_update=true 时，三个数组必须表示「Agent 自动提炼」区的完整新版本

## 输出格式
严格输出 JSON：
{
  "should_update": true,
  "preferences": ["..."],
  "facts": ["..."],
  "constraints": ["..."]
}

如果不需要更新：
{
  "should_update": false,
  "preferences": [],
  "facts": [],
  "constraints": []
}"""


async def extract_and_save_memories(
    db: DBSession,
    user_id: str,
    user_message: str,
    assistant_message: str,
) -> list[dict]:
    """从一轮对话中提取自动记忆并更新 markdown 档案。"""
    if not user_message or not assistant_message:
        return []

    client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    profile = ensure_memory_profile(db, user_id)
    current_sections, _ = parse_memory_profile(profile.content_md)

    user_content = (
        "【当前用户手动添加区】\n"
        f"{json.dumps(current_sections['MANUAL'], ensure_ascii=False)}\n\n"
        "【当前 Agent 自动提炼区】\n"
        f"{json.dumps(current_sections['AUTO'], ensure_ascii=False)}\n\n"
        f"【本轮用户消息】\n{user_message}\n\n"
        f"【本轮助手回复】\n{assistant_message}"
    )

    messages = [
        {"role": "system", "content": EXTRACT_PROMPT},
        {"role": "user", "content": user_content},
    ]

    try:
        resp = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0,
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        extracted = json.loads(raw)
    except Exception as e:
        logger.warning("记忆提取失败: %s | user_message=%s", e, user_message[:100])
        return []
    finally:
        await client.close()

    if not isinstance(extracted, dict) or not extracted.get("should_update"):
        return []

    sections = normalize_memory_sections({
        "MANUAL": current_sections["MANUAL"],
        "AUTO": {
            "PREFERENCE": extracted.get("preferences", current_sections["AUTO"]["PREFERENCE"]),
            "FACT": extracted.get("facts", current_sections["AUTO"]["FACT"]),
            "CONSTRAINT": extracted.get("constraints", current_sections["AUTO"]["CONSTRAINT"]),
        },
    })
    new_content = render_memory_profile(sections)

    try:
        _, changed = save_memory_profile_content(db, profile, new_content)
    except ValueError as e:
        logger.warning("记忆档案保存失败: %s", e)
        return []

    if not changed:
        return []

    saved: list[dict] = []
    for memory_type, items in sections["AUTO"].items():
        saved.extend(
            {
                "content": item,
                "memory_type": memory_type,
                "source": "AUTO",
                "is_stale": False,
            }
            for item in items
        )
    return saved
