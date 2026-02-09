"""
MCP Client Implementation for PassAgent
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class PassAgentMCPClient:
    """PassAgent MCP客户端"""

    def __init__(self, server_url: str = None):
        self.server_url = (
            server_url
            or f"http://{settings.mcp_server_host}:{settings.mcp_server_port}"
        )
        self.client = None
        self.available_tools = {}
        self._connected = False

    async def _ensure_client(self):
        """确保客户端已初始化"""
        if self.client is None or self.client.is_closed:
            self.client = httpx.AsyncClient(timeout=30.0)

    async def connect(self):
        """连接到MCP服务器"""
        try:
            # 确保客户端已初始化
            await self._ensure_client()

            # 检查服务器健康状态
            response = await self.client.get(f"{self.server_url}/health")
            if response.status_code == 200:
                self._connected = True
                logger.info(f"MCP客户端连接成功: {self.server_url}")
            else:
                raise ConnectionError(f"MCP服务器响应异常: {response.status_code}")

        except Exception as e:
            logger.error(f"MCP客户端连接失败: {str(e)}")
            self._connected = False
            raise

    async def disconnect(self):
        """断开连接"""
        if self.client and not self.client.is_closed:
            await self.client.aclose()
            self._connected = False
            logger.info("MCP客户端已断开连接")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """调用指定工具"""
        print(f"call_tool 被调用了! 工具名: {tool_name}")

        # 确保客户端已初始化
        await self._ensure_client()

        if not self._connected:
            await self.connect()

        try:
            print(f"调用工具: {tool_name} with arguments: {arguments}")
            response = await self.client.post(
                f"{self.server_url}/tools/{tool_name}",
                json=arguments,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                return response.json()
            else:
                error_text = (
                    response.text
                    if hasattr(response, "text")
                    else str(response.status_code)
                )
                raise Exception(f"工具调用失败: {response.status_code} - {error_text}")

        except httpx.RequestError as e:
            logger.error(f"网络请求失败 {tool_name}: {str(e)}")
            # 重置连接状态，下次调用时重新连接
            self._connected = False
            raise Exception(f"网络连接失败: {str(e)}")
        except Exception as e:
            logger.error(f"工具调用失败 {tool_name}: {str(e)}")
            raise

    async def analyze_password_with_tools(self, password: str) -> Dict[str, Any]:
        """使用多个工具综合分析密码"""
        try:
            result = await self.call_tool(
                "analyze_password_comprehensive",
                {"password": password, "include_suggestions": True},
            )

            if result.get("status") == "success":
                return result
            else:
                return {"error": result.get("error", "分析失败")}

        except Exception as e:
            logger.error(f"综合分析失败: {str(e)}")
            return {"error": str(e)}

    async def generate_smart_password(self, request_type: str, **kwargs) -> str:
        """智能生成密码"""
        try:
            tool_mapping = {
                "text": "generate_password_from_text",
                "image": "analyze_image_for_password",
                "location": "generate_location_password",
            }

            tool_name = tool_mapping.get(request_type)
            if not tool_name:
                raise ValueError(f"不支持的生成类型: {request_type}")

            result = await self.call_tool(tool_name, kwargs)

            if result.get("status") == "success":
                return result.get("response", "密码生成失败")
            else:
                raise Exception(result.get("error", "密码生成失败"))

        except Exception as e:
            logger.error(f"智能密码生成失败: {str(e)}")
            raise

    async def classify_user_intent(self, message: str) -> Dict[str, Any]:
        """分类用户意图"""
        try:
            result = await self.call_tool("classify_intent", {"message": message})

            if result.get("status") == "success":
                print(f"意图分类结果: {result}")

                return {
                    "intent": result.get("intent", "general_chat"),
                    "confidence": result.get("confidence", 0.0),
                }
            else:
                return {"intent": "general_chat", "confidence": 0.0}

        except Exception as e:
            logger.error(f"意图分类失败: {str(e)}")
            return {"intent": "general_chat", "confidence": 0.0}

    async def batch_analyze_passwords(self, passwords: List[str]) -> Dict[str, Any]:
        """批量分析密码"""
        try:
            result = await self.call_tool(
                "batch_analyze_passwords", {"passwords": passwords}
            )

            if result.get("status") == "success":
                return result
            else:
                return {"error": result.get("error", "批量分析失败")}

        except Exception as e:
            logger.error(f"批量分析失败: {str(e)}")
            return {"error": str(e)}
        
    async def check_password_leak(self, password: str) -> Dict[str, Any]:
        """检测密码是否泄露"""
        try:
            result = await self.call_tool("check_password_leak", {"password": password})
            
            if result.get("status") == "success":
                print(f"密码泄露检测结果: {result.get('message')}")
                return result
            else:
                return {"error": result.get("error", "泄露检测失败")}

        except Exception as e:
            logger.error(f"密码泄露检测失败: {str(e)}")
            return {"error": str(e)}

    async def batch_check_password_leak(self, passwords: List[str]) -> Dict[str, Any]:
        """批量检测密码泄露"""
        try:
            result = await self.call_tool("batch_check_password_leak", {"passwords": passwords})
            
            if result.get("status") == "success":
                print(f"批量泄露检测完成: {result.get('summary')}")
                return result
            else:
                return {"error": result.get("error", "批量泄露检测失败")}

        except Exception as e:
            logger.error(f"批量密码泄露检测失败: {str(e)}")
            return {"error": str(e)}
    
    async def get_security_advice(self, query: str) -> str:
        """获取安全建议"""
        try:
            result = await self.call_tool("get_security_advice", {"query": query})
            
            if result.get("status") == "success":
                advice = result.get("advice", "暂无建议")
                source = result.get("source", "")
                note = result.get("note", "")
                
                response = f"**💡 安全建议 ({source})**\n\n"
                if note:
                    response += f"*{note}*\n\n"
                response += advice
                
                return response
            else:
                return f"获取安全建议失败: {result.get('error', '未知错误')}"

        except Exception as e:
            logger.error(f"获取安全建议失败: {str(e)}")
            return "安全建议服务暂时不可用，请稍后重试。"
        
    async def extract_passwords(self, user_input: str, intent: str = None) -> Dict[str, Any]:
        """提取用户输入中的密码"""
        try:
            result = await self.call_tool(
                "extract_passwords", 
                {"user_input": user_input, "intent": intent}
            )
            
            if result.get("status") == "success":
                passwords = result.get("passwords", [])
                print(f"提取到 {len(passwords)} 个密码")
                return result
            else:
                return {"error": result.get("error", "密码提取失败")}

        except Exception as e:
            logger.error(f"密码提取失败: {str(e)}")
            return {"error": str(e)}

    async def __aenter__(self):
        await self._ensure_client()
        if not self._connected:
            await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # 保持连接以供复用，不关闭客户端
        pass


# 全局MCP客户端实例
mcp_client = PassAgentMCPClient()
