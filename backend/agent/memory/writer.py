"""记忆写入：从对话中自动提取记忆并持久化

实现：
- LLM 提取 → embedding → 语义冲突检测 → 存 DB
- 语义去重（sim > 0.92 跳过）
- 冲突检测（0.85 < sim ≤ 0.92 替换旧记忆）
- LRU 淘汰（每用户最多 200 条，超限按 last_accessed_at 淘汰）
"""
from __future__ import annotations

import json
import logging
import uuid

from openai import AsyncOpenAI
from sqlalchemy.orm import Session as DBSession

logger = logging.getLogger(__name__)

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from database.models import UserMemory
from agent.memory.embedding import (
    get_embedding,
    embedding_to_bytes,
    bytes_to_embedding,
    cosine_similarity,
)

# 每用户最大记忆条数
MAX_MEMORIES_PER_USER = 200
# 语义相似度阈值
DEDUP_THRESHOLD = 0.92      # sim > 0.92 → 视为重复，跳过写入
CONFLICT_THRESHOLD = 0.85   # 0.85 < sim ≤ 0.92 → 视为冲突，替换旧记忆

EXTRACT_PROMPT = """\
你是一个记忆提取器。从用户的对话中提取值得长期记住的个人信息。

## 记忆类型
- PREFERENCE: 用户偏好（如"喜欢用特殊字符"、"密码长度偏好16位"）
- FACT: 个人事实（如"生日是1995年3月"、"养了一只叫Mimi的猫"、"常用邮箱是xxx"、"女朋友叫小红"、"喜欢篮球"）
- CONSTRAINT: 约束条件（如"公司要求密码每90天更换"、"不能包含用户名"）

## 规则
1. 提取所有可能用于个性化口令生成的个人信息，包括但不限于：宠物名、人名、昵称、生日、纪念日、爱好、常用网站、邮箱、手机号等
2. 不要提取临时性的、一次性的操作指令（如"帮我检测这个密码"、"你好"）
3. 每条记忆应该是独立的、简洁的陈述句
4. 宁可多提取，也不要遗漏有价值的个人信息
5. 如果没有值得提取的信息，返回空数组
6. **绝不存储明文密码或密码哈希**。即使用户在对话中提供了密码用于评估，也只提取密码中透露出的个人信息事实（如"用女儿名字做的密码"→提取"女儿名字相关"），而非密码本身
7. 记忆线索采用模糊化存储策略，仅记录语义类别（如"家人相关"、"日期相关"），不记录具体密码内容

## 输出格式
返回 JSON 数组，每个元素：{"content": "...", "memory_type": "PREFERENCE|FACT|CONSTRAINT"}
如果没有可提取的记忆，返回 []"""


def _now_iso() -> str:
    from utils.timezone import beijing_now_iso
    return beijing_now_iso()


def _find_semantic_match(
    new_vec: list[float],
    existing: list[UserMemory],
) -> tuple[str, UserMemory | None]:
    """在同类型已有记忆中查找语义最相似的。

    Returns:
        ("duplicate", mem) — sim > DEDUP_THRESHOLD，应跳过
        ("conflict", mem)  — CONFLICT_THRESHOLD < sim ≤ DEDUP_THRESHOLD，应替换
        ("new", None)      — 无冲突，正常写入
    """
    best_sim = 0.0
    best_mem: UserMemory | None = None

    for m in existing:
        if not m.embedding:
            continue
        mem_vec = bytes_to_embedding(m.embedding)
        sim = cosine_similarity(new_vec, mem_vec)
        if sim > best_sim:
            best_sim = sim
            best_mem = m

    if best_sim > DEDUP_THRESHOLD:
        return "duplicate", best_mem
    if best_sim > CONFLICT_THRESHOLD:
        return "conflict", best_mem
    return "new", None


def _evict_lru(db: DBSession, user_id: str) -> None:
    """当用户记忆数超过上限时，按 LRU 淘汰 last_accessed_at 最早的记忆。"""
    count = db.query(UserMemory).filter(UserMemory.user_id == user_id).count()
    if count <= MAX_MEMORIES_PER_USER:
        return

    overflow = count - MAX_MEMORIES_PER_USER
    # last_accessed_at 为 NULL 的排在最前面（从未被访问过的最先淘汰）
    oldest = (
        db.query(UserMemory)
        .filter(UserMemory.user_id == user_id)
        .order_by(
            UserMemory.last_accessed_at.is_(None).desc(),
            UserMemory.last_accessed_at.asc(),
        )
        .limit(overflow)
        .all()
    )
    for m in oldest:
        db.delete(m)
    logger.info("LRU 淘汰 %d 条记忆 (user=%s)", len(oldest), user_id)


async def extract_and_save_memories(
    db: DBSession,
    user_id: str,
    user_message: str,
    assistant_message: str,
) -> list[dict]:
    """从一轮对话中提取记忆并保存到数据库。

    流程：
    1. LLM 提取候选记忆
    2. 对每条候选生成 embedding
    3. 在同类型已有记忆中做语义匹配：
       - sim > 0.92 → 跳过（重复）
       - 0.85 < sim ≤ 0.92 → 替换旧记忆（冲突，Last Write Wins）
       - sim ≤ 0.85 → 新增
    4. 检查并执行 LRU 淘汰

    Returns:
        新保存/更新的记忆列表
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
    except Exception as e:
        logger.warning("记忆提取失败: %s | user_message=%s", e, user_message[:100])
        return []

    if not isinstance(extracted, list) or not extracted:
        return []

    # 预加载该用户所有记忆（用于冲突检测）
    all_memories = (
        db.query(UserMemory)
        .filter(UserMemory.user_id == user_id)
        .all()
    )
    # 按类型分组
    memories_by_type: dict[str, list[UserMemory]] = {
        "PREFERENCE": [],
        "FACT": [],
        "CONSTRAINT": [],
    }
    for m in all_memories:
        if m.memory_type in memories_by_type:
            memories_by_type[m.memory_type].append(m)

    now = _now_iso()
    saved: list[dict] = []

    for item in extracted:
        content = item.get("content", "").strip()
        memory_type = item.get("memory_type", "FACT")
        if not content or memory_type not in ("PREFERENCE", "FACT", "CONSTRAINT"):
            continue

        # 精确去重（兜底）
        exists_exact = any(
            m.content == content for m in memories_by_type.get(memory_type, [])
        )
        if exists_exact:
            continue

        # 生成 embedding
        vec = await get_embedding(content)
        emb_bytes = embedding_to_bytes(vec) if vec else None

        # 语义冲突检测
        if vec is not None:
            match_type, matched_mem = _find_semantic_match(
                vec, memories_by_type.get(memory_type, [])
            )
        else:
            match_type, matched_mem = "new", None

        if match_type == "duplicate":
            logger.debug("语义去重：跳过 '%s'（与 '%s' 重复）", content, matched_mem.content if matched_mem else "?")
            continue

        if match_type == "conflict" and matched_mem is not None:
            # Last Write Wins：用新内容替换旧记忆
            logger.info(
                "语义冲突替换：'%s' → '%s' (memory_id=%s)",
                matched_mem.content, content, matched_mem.memory_id,
            )
            matched_mem.content = content
            matched_mem.embedding = emb_bytes
            matched_mem.created_at = now
            matched_mem.last_accessed_at = now
            matched_mem.access_count = 0
            matched_mem.is_stale = 0
            saved.append({
                "memory_id": matched_mem.memory_id,
                "content": content,
                "memory_type": memory_type,
                "source": "auto",
                "action": "replaced",
            })
            continue

        # 正常新增
        memory_id = str(uuid.uuid4())
        memory = UserMemory(
            memory_id=memory_id,
            user_id=user_id,
            content=content,
            memory_type=memory_type,
            source="auto",
            embedding=emb_bytes,
            access_count=0,
            is_stale=0,
            last_accessed_at=now,
            created_at=now,
        )
        db.add(memory)
        # 同步更新本地缓存以便后续记忆的冲突检测能看到
        memories_by_type[memory_type].append(memory)
        saved.append({
            "memory_id": memory_id,
            "content": content,
            "memory_type": memory_type,
            "source": "auto",
            "action": "created",
        })

    if saved:
        # LRU 淘汰检查
        _evict_lru(db, user_id)
        db.commit()

    return saved
