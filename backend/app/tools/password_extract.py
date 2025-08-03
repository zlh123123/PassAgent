"""
MCP Tool: 密码提取
使用 DeepSeek API 从用户输入中智能提取密码
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class PasswordExtractorClient:
    """密码提取客户端 - 基于 DeepSeek"""

    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = "https://api.deepseek.com"
        self.model = "deepseek-chat"

    async def extract_passwords(self, user_input: str) -> List[str]:
        """从用户输入中提取密码"""
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
                    "messages": self._build_extraction_messages(user_input),
                    "temperature": 0.1,
                    "max_tokens": 300,
                },
                timeout=30.0,
            )

            if response.status_code == 200:
                result = response.json()
                return self._parse_passwords(result["choices"][0]["message"]["content"])
            else:
                raise Exception(f"DeepSeek API 调用失败: {response.status_code}")

    def _build_extraction_messages(self, user_input: str) -> list:
        """构建密码提取的对话消息"""
        system_prompt = """你是一个专业的密码提取工具。你的任务是从用户输入中准确识别和提取密码。

**提取规则：**
1. 识别明显的密码字符串（包含字母、数字、特殊字符的组合）
2. 排除明显的示例密码（如 "password123", "123456" 等常见弱密码示例）
3. 识别用引号、括号或其他标记包围的密码
4. 考虑上下文语境判断是否为真实密码

**输出格式：**
请以JSON数组格式返回提取到的密码，只返回JSON，不要其他内容：
["password1", "password2", ...]

如果没有找到密码，返回空数组：[]

**注意事项：**
- 只提取疑似真实密码，不包含明显的示例
- 保持密码的原始格式
- 如果用户明确说这是示例，则不提取"""

        user_message = f"""请从以下用户输入中提取密码：

用户输入：{user_input}

请仔细分析并提取其中可能的密码。"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

    def _parse_passwords(self, response_text: str) -> List[str]:
        """解析API响应中的密码"""
        try:
            # 尝试解析JSON数组
            json_match = re.search(r"\[.*?\]", response_text, re.DOTALL)
            if json_match:
                passwords = json.loads(json_match.group())
                return [
                    pwd for pwd in passwords if isinstance(pwd, str) and pwd.strip()
                ]

            # 如果没有找到JSON格式，尝试其他解析方式
            passwords = []
            lines = response_text.split("\n")
            for line in lines:
                line = line.strip()
                if line and not line.startswith(("*", "-", "•", "1.", "2.", "3.")):
                    # 移除引号
                    line = line.strip("\"'")
                    if len(line) >= 6:  # 最小密码长度
                        passwords.append(line)

            return passwords

        except Exception as e:
            logger.error(f"解析密码响应失败: {str(e)}")
            return []


# 全局密码提取客户端实例
password_extractor_client = PasswordExtractorClient()


async def extract_passwords_tool(user_input: str, intent: str = None) -> Dict[str, Any]:
    """MCP Tool: 从用户输入中提取密码"""
    print(f"接收到密码提取请求，意图: {intent}")

    try:
        if not user_input:
            return {"status": "error", "error": "用户输入不能为空"}

        # 首先尝试规则提取（快速路径）
        rule_passwords = _extract_passwords_by_rules(user_input)

        # 如果规则提取到密码，直接返回
        if rule_passwords:
            return {
                "status": "success",
                "passwords": rule_passwords,
                "method": "rule_based",
                "count": len(rule_passwords),
                "message": f"通过规则提取到 {len(rule_passwords)} 个密码",
            }

        # 如果规则提取失败，使用AI提取
        try:
            ai_passwords = await password_extractor_client.extract_passwords(user_input)

            if ai_passwords:
                return {
                    "status": "success",
                    "passwords": ai_passwords,
                    "method": "ai_based",
                    "count": len(ai_passwords),
                    "message": f"通过AI提取到 {len(ai_passwords)} 个密码",
                }
            else:
                return {
                    "status": "success",
                    "passwords": [],
                    "method": "none",
                    "count": 0,
                    "message": "未在输入中发现密码",
                }

        except Exception as e:
            logger.error(f"AI密码提取失败，使用规则提取: {str(e)}")
            # AI失败时的降级处理
            return {
                "status": "success",
                "passwords": rule_passwords,
                "method": "rule_fallback",
                "count": len(rule_passwords),
                "message": "AI服务不可用，使用规则提取",
                "note": "建议稍后重试以获得更准确的结果",
            }

    except Exception as e:
        logger.error(f"密码提取失败: {str(e)}")
        return {"status": "error", "error": f"提取失败: {str(e)}"}


def _extract_passwords_by_rules(user_input: str) -> List[str]:
    """基于规则的密码提取（降级方案）"""
    passwords = []

    # 规则1: 引号内的内容
    quote_patterns = [
        r'"([^"]{6,})"',  # 双引号
        r"'([^']{6,})'",  # 单引号
        r"`([^`]{6,})`",  # 反引号
    ]

    for pattern in quote_patterns:
        matches = re.findall(pattern, user_input)
        for match in matches:
            if _is_likely_password(match):
                passwords.append(match)

    # 规则2: 明确标识的密码
    password_patterns = [
        r"密码[:：]\s*([^\s]{6,})",
        r"password[:：]\s*([^\s]{6,})",
        r"口令[:：]\s*([^\s]{6,})",
        r"pwd[:：]\s*([^\s]{6,})",
    ]

    for pattern in password_patterns:
        matches = re.findall(pattern, user_input, re.IGNORECASE)
        for match in matches:
            if _is_likely_password(match):
                passwords.append(match)

    # 规则3: 括号内的内容
    bracket_patterns = [
        r"\(([^)]{6,})\)",  # 圆括号
        r"\[([^\]]{6,})\]",  # 方括号
        r"\{([^}]{6,})\}",  # 花括号
    ]

    for pattern in bracket_patterns:
        matches = re.findall(pattern, user_input)
        for match in matches:
            if _is_likely_password(match):
                passwords.append(match)

    # 去重并返回
    return list(set(passwords))


def _is_likely_password(text: str) -> bool:
    """判断文本是否可能是密码"""
    if len(text) < 6 or len(text) > 128:
        return False

    # 排除明显的非密码内容
    exclude_patterns = [
        r"^[a-zA-Z\s]+$",  # 只有字母和空格
        r"^\d+$",  # 只有数字
        r"^[^a-zA-Z0-9]+$",  # 只有特殊字符
    ]

    for pattern in exclude_patterns:
        if re.match(pattern, text):
            return False

    # 排除常见示例密码
    common_examples = [
        "password",
        "password123",
        "123456",
        "admin",
        "user123",
        "example",
        "sample",
        "test123",
        "demo",
        "your_password",
    ]

    if text.lower() in common_examples:
        return False

    # 检查是否包含多种字符类型
    has_letter = bool(re.search(r"[a-zA-Z]", text))
    has_digit = bool(re.search(r"\d", text))
    has_special = bool(re.search(r"[^a-zA-Z0-9]", text))

    # 至少包含两种类型的字符
    char_types = sum([has_letter, has_digit, has_special])

    return char_types >= 2
