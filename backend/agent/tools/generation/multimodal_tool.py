"""multimodal_parse 工具：调用 SiliconFlow Qwen3-Omni 将上传的图片/音频转为文本关键词

通过 SiliconFlow OpenAI 兼容 API 调用 Qwen3-Omni-30B-A3B-Captioner 模型，
从图片或音频中提取可用于口令生成的关键词，并将解析结果回写 UploadedFile.extracted_text。
"""
from __future__ import annotations

import base64
import logging
import mimetypes
import os

import httpx

from agent.graph import register_tool
from agent.state import PassAgentState
from config import OMNI_BASE_URL, OMNI_MODEL, EMBEDDING_API_KEY

logger = logging.getLogger(__name__)

# SiliconFlow API（与 Embedding 共用同一平台的 Key）
_API_BASE = OMNI_BASE_URL  # https://api.siliconflow.cn/v1
_API_KEY = EMBEDDING_API_KEY
_MODEL = OMNI_MODEL  # Qwen/Qwen3-Omni-30B-A3B-Captioner
_TIMEOUT = 90  # 多模态推理较慢，给足时间

_EXTRACT_PROMPT = """You are a passphrase generation assistant. Please extract 5-10 meaningful keywords or phrases from the following content. These keywords will be used as seed material for passphrase generation. Requirements:
1. Keywords should be distinctive and personally relevant
2. Include specific object names, locations, colors, emotions, etc.
3. Output each keyword on a separate line
4. Only output the keyword list, no other explanations"""


def _file_to_base64(file_path: str) -> str:
    """将文件读取为 base64 字符串。"""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _build_messages(file_path: str, file_type: str) -> list[dict]:
    """根据文件类型构建 SiliconFlow Qwen3-Omni 兼容的多模态消息。"""
    mime = file_type or mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    b64 = _file_to_base64(file_path)

    if mime.startswith("image/"):
        # SiliconFlow VLM 格式：image_url
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    },
                    {"type": "text", "text": _EXTRACT_PROMPT},
                ],
            }
        ]
    elif mime.startswith("audio/"):
        # SiliconFlow Qwen3-Omni Audio 格式：input_audio
        fmt = mime.split("/")[-1]
        # 统一格式名：mpeg→mp3
        if fmt == "mpeg":
            fmt = "mp3"
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "input_audio": {"data": b64, "format": fmt},
                    },
                    {"type": "text", "text": _EXTRACT_PROMPT},
                ],
            }
        ]
    else:
        raise ValueError(f"不支持的文件类型: {mime}")


async def parse_multimodal(file_path: str, file_type: str) -> dict:
    """调用 SiliconFlow Qwen3-Omni 多模态模型提取关键词。

    Returns:
        {"keywords": [...], "raw_response": "...", "file_type": "..."}
    """
    if not os.path.exists(file_path):
        return {"error": f"文件不存在: {file_path}", "keywords": []}

    messages = _build_messages(file_path, file_type)

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{_API_BASE}/chat/completions",
            json={
                "model": _MODEL,
                "messages": messages,
                "max_tokens": 512,
                "temperature": 0.3,
                "top_p": 0.7,
            },
            headers={
                "Authorization": f"Bearer {_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"]["content"]
    # 解析关键词（每行一个，去掉序号前缀）
    keywords = [
        line.strip().lstrip("0123456789.-) ")
        for line in content.strip().splitlines()
    ]
    keywords = [k for k in keywords if k and len(k) < 50]

    return {
        "keywords": keywords,
        "raw_response": content,
        "file_type": file_type,
    }


def _save_extracted_text(file_id: str, extracted_text: str) -> None:
    """将解析结果回写到 UploadedFile.extracted_text（同步 DB 操作）。"""
    from database.connection import SessionLocal
    from database.models import UploadedFile

    db = SessionLocal()
    try:
        record = db.query(UploadedFile).filter(UploadedFile.file_id == file_id).first()
        if record:
            record.extracted_text = extracted_text
            db.commit()
    except Exception as e:
        logger.warning("回写 extracted_text 失败 (file_id=%s): %s", file_id, e)
        db.rollback()
    finally:
        db.close()


@register_tool("multimodal_parse")
async def multimodal_parse_tool(state: PassAgentState) -> dict:
    """将上传的图片/音频文件转为文本关键词，并回写 extracted_text 到数据库。"""
    params = state.get("action_params", {})
    file_path = params.get("file_path", "")
    file_type = params.get("file_type", "")
    file_id = params.get("file_id", "")

    try:
        result = await parse_multimodal(file_path, file_type)
    except httpx.HTTPStatusError as e:
        result = {"keywords": [], "error": f"模型服务请求失败: {e.response.status_code}"}
    except httpx.RequestError as e:
        result = {"keywords": [], "error": f"网络请求失败: {str(e)}"}
    except ValueError as e:
        result = {"keywords": [], "error": str(e)}

    # 将原始解析结果回写到 UploadedFile.extracted_text
    if file_id and "error" not in result:
        extracted = result.get("raw_response", "")
        _save_extracted_text(file_id, extracted)

    return {"_tool_result": result}
