"""文本向量化：调用 Embedding API 生成向量 & 余弦相似度计算"""
from __future__ import annotations

import struct
from openai import AsyncOpenAI

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

# DeepSeek 目前不提供 embedding 端点，可切换为其他兼容服务
# 如果 EMBEDDING_MODEL 为空则回退到关键词匹配（reader 中处理）
EMBEDDING_MODEL = "text-embedding-ada-002"  # 按实际可用模型替换
EMBEDDING_DIM = 1536


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


async def get_embedding(text: str) -> list[float] | None:
    """获取文本的 embedding 向量，失败时返回 None。"""
    try:
        client = _get_client()
        resp = await client.embeddings.create(model=EMBEDDING_MODEL, input=text)
        return resp.data[0].embedding
    except Exception:
        return None


def embedding_to_bytes(vec: list[float]) -> bytes:
    """将 float 列表序列化为 bytes（存入 SQLite LargeBinary）。"""
    return struct.pack(f"{len(vec)}f", *vec)


def bytes_to_embedding(data: bytes) -> list[float]:
    """将 bytes 反序列化为 float 列表。"""
    n = len(data) // 4
    return list(struct.unpack(f"{n}f", data))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """计算两个向量的余弦相似度。"""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
