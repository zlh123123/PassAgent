"""记忆写入：从对话中自动提取记忆并持久化"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from openai import AsyncOpenAI
from sqlalchemy.orm import Session as DBSession

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from database.models import UserMemory
from agent.memory.embedding import get_embedding, embedding_to_bytes

EXTRACT_PROMPT = """\
你是一个记忆提取器。从用户的对话中提取值得长期记住的信息。

## 记忆类型
- PREFERENCE: 用户偏好（如"喜欢用特殊字符"、"密码长度偏好16位"）
- FACT: 个人事实（如"生日是1995年3月"、"养了一只叫Mimi的猫"、"常用邮箱是xxx"）
- CONSTRAINT: 约束条件（如"公司要求密码每90天更换"、"不能包含用户名"）

## 规则
1. 只提取与口令安全相关的、值得长期记住的信息
2. 不要提取临时性的、一次性的信息（如"帮我检测这个密码"）
3. 每条记忆应该是独立的、简洁的陈述句
4. 如果没有值得提取的信息，返回空数组

## 输出格式
返回 JSON 数组，每个元素：{"content": "...", "memory_type": "PREFERENCE|FACT|CONSTRAINT"}
如果没有可提取的记忆，返回 []"""


async def extract_and_save_memories(
    db: DBSession,
    user_id: str,
    user_message: str,
    assistant_message: str,
) -> list[dict]:
    """从一轮对话中提取记忆并保存到数据库。

    Returns:
        新保存的记忆列表
    """
    client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    messages = [
        {"role": "system", "content": EXTRACT_PROMPT},
        {
            "role": "user",
            "content": f"用户消息：{user_message}\n助手回复：{assistant_message}",
        },
    ]

    try:
        resp = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0,
        )
        raw = resp.choices[0].message.content.strip()
        # 处理可能的 markdown 代码块包裹
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        extracted = json.loads(raw)
    except Exception:
        return []

    if not isinstance(extracted, list) or not extracted:
        return []

    saved: list[dict] = []
    for item in extracted:
        content = item.get("content", "").strip()
        memory_type = item.get("memory_type", "FACT")
        if not content or memory_type not in ("PREFERENCE", "FACT", "CONSTRAINT"):
            continue

        # 去重：相同内容不重复存储
        exists = (
            db.query(UserMemory)
            .filter(
                UserMemory.user_id == user_id,
                UserMemory.content == content,
            )
            .first()
        )
        if exists:
            continue

        memory_id = str(uuid.uuid4())

        # 生成 embedding（异步，失败不阻塞）
        vec = await get_embedding(content)
        emb_bytes = embedding_to_bytes(vec) if vec else None

        memory = UserMemory(
            memory_id=memory_id,
            user_id=user_id,
            content=content,
            memory_type=memory_type,
            source="auto",
            embedding=emb_bytes,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        db.add(memory)
        saved.append({
            "memory_id": memory_id,
            "content": content,
            "memory_type": memory_type,
            "source": "auto",
        })

    if saved:
        db.commit()

    return saved
