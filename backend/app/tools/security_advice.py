"""
MCP Tool: 密码安全建议
使用 DeepSeek API 提供专业的密码安全建议
"""

import json
import logging
import re
from typing import Dict, Any
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class SecurityAdvisorClient:
    """安全建议客户端 - 基于 DeepSeek"""

    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = "https://api.deepseek.com"
        self.model = "deepseek-chat"

    async def get_security_advice(self, query: str) -> str:
        """获取安全建议"""
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
                    "messages": self._build_security_messages(query),
                    "temperature": 0.3,
                    "max_tokens": 1000,
                },
                timeout=30.0,
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(f"DeepSeek API 调用失败: {response.status_code}")

    def _build_security_messages(self, query: str) -> list:
        """构建安全建议的对话消息"""
        system_prompt = """你是一个专业的网络安全专家和密码安全顾问。你的任务是为用户提供准确、实用、易懂的密码安全建议。

**你的专业领域包括：**
- 密码安全最佳实践
- 账户安全防护
- 两步验证设置
- 密码管理器使用
- 社会工程学防范
- 数据泄露应对
- 企业安全策略
- 个人隐私保护

**回复格式要求：**
- 使用清晰的结构化格式
- 提供具体可操作的建议
- 包含风险等级评估
- 适当使用表情符号增强可读性
- 避免过于技术性的术语，用通俗易懂的语言

**回复原则：**
- 准确性：基于最新的安全标准和最佳实践
- 实用性：提供可立即执行的具体步骤
- 全面性：考虑不同场景和风险级别
- 个性化：根据用户具体情况提供定制建议"""

        user_message = f"""请针对以下密码安全相关问题提供专业建议：

用户问题：{query}

请提供结构化的安全建议，包括：
1. 风险评估
2. 具体建议
3. 实施步骤
4. 注意事项"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]


# 全局安全建议客户端实例
security_advisor_client = SecurityAdvisorClient()


async def get_security_advice_tool(query: str) -> Dict[str, Any]:
    """MCP Tool: 获取密码安全建议"""
    print(f"接收到安全建议请求: {query}")

    try:
        if not query:
            return {"status": "error", "error": "查询内容不能为空"}

        # 调用 DeepSeek API 获取安全建议
        advice_content = await security_advisor_client.get_security_advice(query)

        return {
            "status": "success",
            "advice": advice_content,
            "query": query,
            "source": "DeepSeek 安全专家",
            "timestamp": "实时生成",
        }

    except Exception as e:
        logger.error(f"获取安全建议失败: {str(e)}")

        # 降级处理：返回基础安全建议
        fallback_advice = _get_fallback_security_advice(query)
        return {
            "status": "success",
            "advice": fallback_advice,
            "query": query,
            "source": "本地安全知识库",
            "note": "AI服务暂时不可用，以下是基础安全建议",
        }


def _get_fallback_security_advice(query: str) -> str:
    """降级安全建议 - 本地知识库"""
    query_lower = query.lower()

    # 根据关键词匹配相应的安全建议
    if any(
        keyword in query_lower
        for keyword in ["密码管理器", "管理器", "password manager"]
    ):
        return """🔐 **密码管理器安全建议**

**推荐的密码管理器：**
• 1Password - 企业级安全，多平台同步
• Bitwarden - 开源免费，功能完善  
• Dashlane - 用户友好，安全监控
• KeePass - 离线存储，完全控制

**使用建议：**
1️⃣ 启用主密码 - 使用长且独特的主密码
2️⃣ 开启两步验证 - 增加额外安全层
3️⃣ 定期备份 - 避免数据丢失
4️⃣ 安全共享 - 与家人安全共享重要账户

**注意事项：**
⚠️ 不要在不安全的网络上同步
⚠️ 定期更新管理器软件版本"""

    elif any(keyword in query_lower for keyword in ["两步", "2fa", "两因素", "验证"]):
        return """🛡️ **两步验证安全建议**

**推荐的验证方式：**
• 认证器应用 (Google Authenticator, Authy)
• 硬件密钥 (YubiKey, Titan Key)
• 生物识别 (指纹, 面部识别)
• 短信验证 (不推荐作为唯一方式)

**设置优先级：**
1️⃣ 邮箱账户 - 其他账户的恢复入口
2️⃣ 银行和支付账户 - 财务安全
3️⃣ 社交媒体账户 - 防止身份盗用
4️⃣ 工作相关账户 - 保护职业信息

**最佳实践：**
✅ 备份恢复代码并安全存储
✅ 使用多种验证方式
✅ 定期检查已授权设备"""

    elif any(
        keyword in query_lower for keyword in ["泄露", "数据泄露", "breach", "hack"]
    ):
        return """🚨 **数据泄露应对建议**

**发现密码泄露后的应急步骤：**
1️⃣ **立即更换密码** - 在所有使用相同密码的网站
2️⃣ **检查账户活动** - 查看异常登录和操作
3️⃣ **启用安全警报** - 接收账户活动通知
4️⃣ **联系客服** - 报告可疑活动

**预防措施：**
🔍 定期检查密码泄露状态
🔒 使用唯一密码策略
📱 启用登录通知
💾 备份重要数据

**推荐工具：**
• HaveIBeenPwned - 检查数据泄露
• 密码强度检测工具
• 账户安全扫描服务"""

    else:
        return """🔐 **密码安全通用建议**

**强密码创建原则：**
• 长度至少12位字符
• 包含大小写字母、数字、特殊符号
• 避免个人信息和常见单词
• 每个账户使用唯一密码

**账户安全最佳实践：**
1️⃣ 启用两步验证
2️⃣ 定期更换重要密码
3️⃣ 监控账户活动
4️⃣ 使用安全的网络连接

**日常安全习惯：**
✅ 不在公共场所输入敏感信息
✅ 及时注销登录会话
✅ 保持软件和系统更新
✅ 谨慎点击邮件链接

如需更具体的建议，请描述您的具体安全需求。"""


async def check_password_rules_tool(content: str) -> Dict[str, Any]:
    """MCP Tool: 检查密码规则合规性"""
    print(f"接收到密码规则检查请求: {content}")

    try:
        if not content:
            return {"status": "error", "error": "检查内容不能为空"}

        # 使用 DeepSeek 分析密码规则合规性
        rule_analysis = await security_advisor_client.get_security_advice(
            f"请分析以下密码或密码策略是否符合安全标准，并提供改进建议：{content}"
        )

        return {
            "status": "success",
            "analysis": rule_analysis,
            "content": content,
            "type": "password_rule_compliance",
        }

    except Exception as e:
        logger.error(f"密码规则检查失败: {str(e)}")
        return {"status": "error", "error": f"规则检查失败: {str(e)}"}
