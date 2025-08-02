"""
MCP Server Implementation for PassAgent
"""
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from app.tools.leak_checker import check_password_leak_tool, batch_check_password_leak_tool
from app.tools.classify_intent import classify_intent_tool
from app.services.password_service import PasswordService
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

class PassAgentMCPServer:
    """PassAgent MCP服务器"""

    def __init__(self):
        self.password_service = PasswordService()
        self.ai_service = AIService()
        self.app = self._create_app()

    def _create_app(self) -> FastAPI:
        """创建FastAPI应用"""
        app = FastAPI(title="PassAgent MCP Server", version="1.0.0")

        @app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "PassAgent MCP Server"}

        @app.post("/tools/analyze_password_comprehensive")
        async def analyze_password_comprehensive(request: Dict[str, Any]):
            password = request.get("password")
            if not password:
                raise HTTPException(status_code=400, detail="密码不能为空")

            try:
                # 强度分析
                strength_result = self.password_service.analyze_strength(
                    password, request.get("include_suggestions", True)
                )

                # 泄露检查
                async with PasswordLeakChecker() as checker:
                    leak_result = await checker.check_password_leak(password)

                return {
                    "strength": strength_result,
                    "leak": leak_result,
                    "status": "success"
                }
            except Exception as e:
                logger.error(f"密码综合分析失败: {str(e)}")
                return {"error": str(e), "status": "failed"}

        @app.post("/tools/generate_password_from_text")
        async def generate_password_from_text(request: Dict[str, Any]):
            try:
                description = request.get("description", "")
                length = request.get("length", 12)
                include_special = request.get("include_special", True)

                response = await self.ai_service.generate_text_response(
                    f"基于以下描述生成安全密码: {description}。"
                    f"要求长度: {length}，包含特殊字符: {include_special}"
                )

                return {"response": response, "status": "success"}
            except Exception as e:
                logger.error(f"文本密码生成失败: {str(e)}")
                return {"error": str(e), "status": "failed"}

        @app.post("/tools/analyze_image_for_password")
        async def analyze_image_for_password(request: Dict[str, Any]):
            try:
                image_data = request.get("image_data")
                prompt = request.get("prompt", "")

                if not image_data:
                    raise ValueError("图片数据不能为空")

                response = await self.ai_service.analyze_image_for_password(
                    image_data, prompt
                )

                return {"response": response, "status": "success"}
            except Exception as e:
                logger.error(f"图像密码分析失败: {str(e)}")
                return {"error": str(e), "status": "failed"}

        @app.post("/tools/generate_location_password")
        async def generate_location_password(request: Dict[str, Any]):
            try:
                locations = request.get("locations", [])
                prompt = request.get("prompt", "")

                response = await self.ai_service.generate_location_based_password(
                    locations, prompt
                )

                return {"response": response, "status": "success"}
            except Exception as e:
                logger.error(f"位置密码生成失败: {str(e)}")
                return {"error": str(e), "status": "failed"}

        @app.post("/tools/classify_intent")
        async def classify_intent(request: Dict[str, Any]):
            try:
                message = request.get("message", "")
                result = await classify_intent_tool(message)
                return result
            except Exception as e:
                logger.error(f"意图分类失败: {str(e)}")
                return {"error": str(e), "status": "failed"}

        @app.post("/tools/batch_analyze_passwords")
        async def batch_analyze_passwords(request: Dict[str, Any]):
            try:
                passwords = request.get("passwords", [])
                if not passwords:
                    raise ValueError("密码列表不能为空")

                async with PasswordLeakChecker() as checker:
                    leak_results = await checker.batch_check_passwords(passwords)

                results = []
                for password in passwords:
                    strength = self.password_service.analyze_strength(password)
                    leak_info = leak_results.get(password, {})
                    results.append({
                        "password": password[:3] + "*" * (len(password) - 3),
                        "strength": strength,
                        "leak_info": leak_info,
                    })

                return {"results": results, "status": "success"}
            except Exception as e:
                logger.error(f"批量密码分析失败: {str(e)}")
                return {"error": str(e), "status": "failed"}
            
        @app.post("/tools/check_password_leak")
        async def check_password_leak(request: Dict[str, Any]):
            """检测单个密码泄露"""
            try:
                password = request.get("password", "")
                result = await check_password_leak_tool(password)
                return result
            except Exception as e:
                logger.error(f"密码泄露检测失败: {str(e)}")
                return {"error": str(e), "status": "failed"}

        @app.post("/tools/batch_check_password_leak")
        async def batch_check_password_leak(request: Dict[str, Any]):
            """批量检测密码泄露"""
            try:
                passwords = request.get("passwords", [])
                result = await batch_check_password_leak_tool(passwords)
                return result
            except Exception as e:
                logger.error(f"批量密码泄露检测失败: {str(e)}")
                return {"error": str(e), "status": "failed"}

        return app
    


    async def _classify_user_intent(self, message: str) -> Dict[str, Any]:
        """分类用户意图"""
        message_lower = message.lower()

        # 密码分析意图
        if any(keyword in message_lower for keyword in ['分析', '检测', '强度', '安全性', '评估']):
            return {"intent": "password_analysis", "confidence": 0.9}

        # 密码生成意图
        elif any(keyword in message_lower for keyword in ['生成', '推荐', '创建', '制作', '建议']):
            return {"intent": "password_generation", "confidence": 0.9}

        # 泄露检查意图
        elif any(keyword in message_lower for keyword in ['泄露', '被盗', '风险', '检查', '查询']):
            return {"intent": "leak_check", "confidence": 0.8}

        # 批量分析意图
        elif any(keyword in message_lower for keyword in ['批量', '多个', '一批', '全部']):
            return {"intent": "batch_analysis", "confidence": 0.8}

        # 普通对话
        else:
            return {"intent": "general_chat", "confidence": 0.6}

    async def run(self, host: str = "localhost", port: int = 3001):
        """启动MCP服务器"""
        import uvicorn
        logger.info(f"Starting PassAgent MCP Server on {host}:{port}")

        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
