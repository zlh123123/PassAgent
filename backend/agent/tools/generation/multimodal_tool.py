"""multimodal_parse 工具：调用 Qwen-Omni 将上传的图片/音频转为文本关键词

通过 OpenAI 兼容 API 调用 vLLM 部署的 Qwen-Omni-7B 模型，
从图片或音频中提取可用于口令生成的关键词。
"""
from __future__ import annotations

import base64
import mimetypes
import os

import httpx

from agent.graph import register_tool
from agent.state import PassAgentState
from config import LLM_BASE_URL, LLM_API_KEY

# Qwen-Omni 模型名（按需加载时使用，可能和主模型不同）
_OMNI_MODEL = os.getenv("OMNI_MODEL", "Qwen2.5-Omni-7B-Instruct")
_TIMEOUT = 60  # 多模态推理较慢

_EXTRACT_PROMPT = """你是口令生成助手。请从以下内容中提取 5-10 个有意义的关键词或短语，
这些关键词将作为口令生成的种子素材。要求：
1. 关键词应该具有辨识度和个人关联性
2. 包括具体的事物名称、地点、颜色、情感等
3. 每个关键词用单独一行输出
4. 只输出关键词列表，不要其他解释"""


def _file_to_base64(file_path: str) -> str:
    """将文件读取为 base64 字符串。"""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _build_messages(file_path: str, file_type: str) -> list[dict]:
    """根据文件类型构建多模态消息。"""
    mime = file_type or mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    b64 = _file_to_base64(file_path)

    if mime.startswith("image/"):
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
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "input_audio": {"data": b64, "format": mime.split("/")[-1]},
                    },
                    {"type": "text", "text": _EXTRACT_PROMPT},
                ],
            }
        ]
    else:
        raise ValueError(f"不支持的文件类型: {mime}")


async def parse_multimodal(file_path: str, file_type: str) -> dict:
    """调用多模态模型提取关键词。"""
    if not os.path.exists(file_path):
        return {"error": f"文件不存在: {file_path}", "keywords": []}

    messages = _build_messages(file_path, file_type)

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{LLM_BASE_URL}/chat/completions",
            json={
                "model": _OMNI_MODEL,
                "messages": messages,
                "max_tokens": 512,
                "temperature": 0.3,
            },
            headers={
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

    content = data["choices"][0]["message"]["content"]
    # 解析关键词（每行一个）
    keywords = [line.strip().lstrip("0123456789.-、） ") for line in content.strip().splitlines()]
    keywords = [k for k in keywords if k and len(k) < 50]

    return {
        "keywords": keywords,
        "raw_response": content,
        "file_type": file_type,
    }


@register_tool("multimodal_parse")
async def multimodal_parse_tool(state: PassAgentState) -> dict:
    """将上传的图片/音频文件转为文本关键词。"""
    params = state.get("action_params", {})
    file_path = params.get("file_path", "")
    file_type = params.get("file_type", "")

    try:
        result = await parse_multimodal(file_path, file_type)
    except httpx.HTTPStatusError as e:
        result = {"keywords": [], "error": f"模型服务请求失败: {e.response.status_code}"}
    except httpx.RequestError as e:
        result = {"keywords": [], "error": f"网络请求失败: {str(e)}"}
    except ValueError as e:
        result = {"keywords": [], "error": str(e)}

    return {"_tool_result": result}
