"""文本向量化：调用 SiliconFlow BGE Embedding API 生成向量 & 余弦相似度计算"""
from __future__ import annotations

import struct
from openai import AsyncOpenAI

from config import EMBEDDING_API_KEY, EMBEDDING_BASE_URL

EMBEDDING_MODEL = "BAAI/bge-large-zh-v1.5"
EMBEDDING_DIM = 1024


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=EMBEDDING_API_KEY, base_url=EMBEDDING_BASE_URL)


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
