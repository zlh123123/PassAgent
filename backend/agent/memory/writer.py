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
DEDUP_THRESHOLD = 0.85      # sim > 0.85 → 视为重复，跳过写入
CONFLICT_THRESHOLD = 0.75   # 0.75 < sim ≤ 0.85 → 视为冲突，替换旧记忆

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
8. 如果提供了【已有记忆】，请对比后跳过已有记忆中已覆盖的信息；若新信息是对已有记忆的修正/补充，在输出中增加 "update_of" 字段（值为已有记忆的原文内容），并将 content 写为最新版本

## 输出格式
返回 JSON 数组，每个元素：{"content": "...", "memory_type": "PREFERENCE|FACT|CONSTRAINT"}
如果是对已有记忆的更新：{"content": "...", "memory_type": "...", "update_of": "原有记忆内容"}
如果没有可提取的记忆，返回 []"""


def _now_iso() -> str:
    from utils.timezone import beijing_now_iso
    return beijing_now_iso()


def _find_semantic_match(
    new_vec: list[float],
    same_type: list[UserMemory],
    all_memories: list[UserMemory] | None = None,
) -> tuple[str, UserMemory | None]:
    """查找语义最相似的已有记忆。

    - 去重检测：在全量记忆（跨类型）中查找，避免同一信息以不同类型重复存储
    - 冲突替换：仅在同类型内查找，确保替换语义一致

    Returns:
        ("duplicate", mem) — sim > DEDUP_THRESHOLD，应跳过
        ("conflict", mem)  — CONFLICT_THRESHOLD < sim ≤ DEDUP_THRESHOLD，应替换（仅同类型）
        ("new", None)      — 无冲突，正常写入
    """
    # 1. 跨类型去重检测
    dedup_pool = all_memories if all_memories is not None else same_type
    best_dedup_sim = 0.0
    best_dedup_mem: UserMemory | None = None
    for m in dedup_pool:
        if not m.embedding:
            continue
        mem_vec = bytes_to_embedding(m.embedding)
        sim = cosine_similarity(new_vec, mem_vec)
        if sim > best_dedup_sim:
            best_dedup_sim = sim
            best_dedup_mem = m

    if best_dedup_sim > DEDUP_THRESHOLD:
        return "duplicate", best_dedup_mem

    # 2. 同类型冲突检测（替换）
    best_conflict_sim = 0.0
    best_conflict_mem: UserMemory | None = None
    for m in same_type:
        if not m.embedding:
            continue
        mem_vec = bytes_to_embedding(m.embedding)
        sim = cosine_similarity(new_vec, mem_vec)
        if sim > best_conflict_sim:
            best_conflict_sim = sim
            best_conflict_mem = m

    if best_conflict_sim > CONFLICT_THRESHOLD:
        return "conflict", best_conflict_mem
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
    1. 预加载已有记忆，构建摘要注入 LLM 提取 prompt
    2. LLM 提取候选记忆（支持 update_of 字段标记更新意图）
    3. 对每条候选生成 embedding
    4. 语义匹配（跨类型去重 + 同类型冲突替换）：
       - sim > DEDUP_THRESHOLD → 跳过（重复）
       - CONFLICT_THRESHOLD < sim ≤ DEDUP_THRESHOLD → 替换旧记忆
       - sim ≤ CONFLICT_THRESHOLD → 新增
    5. 检查并执行 LRU 淘汰

    Returns:
        新保存/更新的记忆列表
    """
    client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    # 预加载已有记忆（用于注入 prompt 和冲突检测）
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

    # 构建已有记忆摘要（注入 prompt，帮助 LLM 做增量提取）
    existing_summary_parts: list[str] = []
    for mtype, mems in memories_by_type.items():
        if mems:
            type_label = {"PREFERENCE": "偏好", "FACT": "事实", "CONSTRAINT": "约束"}[mtype]
            existing_summary_parts.append(
                f"[{type_label}]\n" + "\n".join(f"- {m.content}" for m in mems)
            )

    user_content = f"用户消息：{user_message}\n助手回复：{assistant_message}"
    if existing_summary_parts:
        user_content += "\n\n【已有记忆】\n" + "\n".join(existing_summary_parts)

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
        # 处理可能的 markdown 代码块包裹
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        extracted = json.loads(raw)
    except Exception as e:
        logger.warning("记忆提取失败: %s | user_message=%s", e, user_message[:100])
        return []

    if not isinstance(extracted, list) or not extracted:
        return []

    now = _now_iso()
    saved: list[dict] = []

    for item in extracted:
        content = item.get("content", "").strip()
        memory_type = item.get("memory_type", "FACT")
        update_of = item.get("update_of", "").strip()  # LLM 标记的被更新记忆原文
        if not content or memory_type not in ("PREFERENCE", "FACT", "CONSTRAINT"):
            continue

        # 精确去重：归一化后比较
        content_norm = content.replace(" ", "").rstrip("。？！")
        exists_exact = any(
            (m.content or "").replace(" ", "").rstrip("。？！") == content_norm
            for m in all_memories
        )
        if exists_exact:
            continue

        # 如果 LLM 指出了被更新的记忆，直接查找并替换（精确匹配原文）
        if update_of:
            target_mem = next(
                (m for m in memories_by_type.get(memory_type, []) if m.content == update_of),
                None,
            )
            if target_mem is None:
                # 原文匹配失败，fallthrough 到 embedding 路径
                pass
            else:
                vec = await get_embedding(content)
                emb_bytes = embedding_to_bytes(vec) if vec else None
                logger.info(
                    "LLM指定更新记忆: '%s' → '%s' (memory_id=%s)",
                    target_mem.content, content, target_mem.memory_id,
                )
                target_mem.content = content
                target_mem.embedding = emb_bytes
                target_mem.last_accessed_at = now
                target_mem.is_stale = 0
                # 保留 access_count 和 created_at
                saved.append({
                    "memory_id": target_mem.memory_id,
                    "content": content,
                    "memory_type": memory_type,
                    "source": "auto",
                    "action": "replaced",
                })
                # 同步本地缓存
                memories_by_type[memory_type] = [
                    target_mem if m.memory_id == target_mem.memory_id else m
                    for m in memories_by_type[memory_type]
                ]
                continue

        # 生成 embedding
        vec = await get_embedding(content)
        emb_bytes = embedding_to_bytes(vec) if vec else None

        # 语义冲突检测（跨类型去重 + 同类型冲突替换）
        if vec is not None:
            match_type, matched_mem = _find_semantic_match(
                vec,
                same_type=memories_by_type.get(memory_type, []),
                all_memories=all_memories,
            )
        else:
            match_type, matched_mem = "new", None

        if match_type == "duplicate":
            logger.debug("语义去重：跳过 '%s'（与 '%s' 重复）", content, matched_mem.content if matched_mem else "?")
            continue

        if match_type == "conflict" and matched_mem is not None:
            # Last Write Wins：用新内容替换旧记忆，保留 access_count 和 created_at
            logger.info(
                "语义冲突替换：'%s' → '%s' (memory_id=%s)",
                matched_mem.content, content, matched_mem.memory_id,
            )
            matched_mem.content = content
            matched_mem.embedding = emb_bytes
            matched_mem.last_accessed_at = now
            matched_mem.is_stale = 0
            # 保留 access_count（不清零）、保留 created_at
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
        all_memories.append(memory)
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
