"""
MCP Tool: 意图分类
"""

import json
import logging
import re
from typing import Dict, Any
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """DeepSeek API 客户端"""

    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = "https://api.deepseek.com"
        self.model = "deepseek-chat"

    async def chat_completion(self, messages, temperature: float = 0.1) -> str:
        """调用 DeepSeek 聊天接口"""
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY 未配置")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 500,
                },
                timeout=30.0,
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(f"DeepSeek API 调用失败: {response.status_code}")


deepseek_client = DeepSeekClient()


async def classify_intent_tool(message: str) -> Dict[str, Any]:
    """MCP Tool: 分类用户意图"""
    print(f"接收到意图分类请求: {message}")  # 这样就能看到输出了

    try:
        if not message:
            return {"status": "error", "error": "消息内容不能为空"}

        # 构建提示词
        system_prompt = """你是一个密码管理助手的意图分类器。请根据用户的输入，将其分类为以下意图之一：

1. password_analysis - 用户想要分析密码强度、安全性、评估密码
2. password_generation - 用户想要生成新密码、创建密码
3. password_leak_check - 用户想要检查密码是否泄露
4. security_advice - 用户想要获取安全建议、最佳实践、安全知识
5. password_rule_check - 用户检查口令是否满足某些规则或标准
6. general_chat - 一般聊天、问候、不相关的话题

请以JSON格式返回结果，只返回JSON，不要其他内容：
{
  "intent": "意图类型",
  "confidence": 0.0-1.0的置信度
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请分类这个用户输入：{message}"},
        ]

        # 调用 DeepSeek API
        response_text = await deepseek_client.chat_completion(messages)

        # 解析响应
        try:
            json_match = re.search(r"\{[^}]*\}", response_text)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(response_text)

            return {
                "status": "success",
                "intent": result.get("intent", "general_chat"),
                "confidence": result.get("confidence", 0.5),
            }

        except json.JSONDecodeError:
            # 降级到规则分类
            fallback_result = _fallback_classify(message)
            return {
                "status": "success",
                "intent": fallback_result["intent"],
                "confidence": fallback_result["confidence"],
            }

    except Exception as e:
        logger.error(f"意图分类失败: {str(e)}")
        return {"status": "error", "error": str(e)}


def _fallback_classify(message: str) -> Dict[str, Any]:
    """规则分类降级方案"""
    message_lower = message.lower()

    if any(
        keyword in message_lower
        for keyword in ["分析", "检查", "测试", "评估", "强度", "安全吗"]
    ):
        if any(pwd_word in message_lower for pwd_word in ["密码", "password"]):
            return {"intent": "password_analysis", "confidence": 0.7}

    if any(keyword in message_lower for keyword in ["生成", "创建", "制作", "帮我"]):
        if any(pwd_word in message_lower for pwd_word in ["密码", "password"]):
            return {"intent": "password_generation", "confidence": 0.7}

    return {"intent": "general_chat", "confidence": 0.5}
