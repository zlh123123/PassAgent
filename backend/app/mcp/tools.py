"""
MCP Tools Registry for PassAgent
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """MCP工具定义"""

    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: callable


class MCPToolRegistry:
    """MCP工具注册表"""

    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self._register_default_tools()

    def register_tool(self, tool: MCPTool):
        """注册工具"""
        self.tools[tool.name] = tool
        logger.info(f"注册MCP工具: {tool.name}")

    def get_tool(self, name: str) -> Optional[MCPTool]:
        """获取工具"""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """列出所有工具"""
        return list(self.tools.keys())

    def _register_default_tools(self):
        """注册默认工具"""

        # 密码分析工具
        password_analysis_tool = MCPTool(
            name="analyze_password_comprehensive",
            description="全面分析密码强度和泄露情况",
            input_schema={
                "type": "object",
                "properties": {
                    "password": {"type": "string", "description": "要分析的密码"},
                    "include_suggestions": {
                        "type": "boolean",
                        "description": "是否包含建议",
                        "default": True,
                    },
                },
                "required": ["password"],
            },
            handler=None,  # 由服务器端点处理
        )
        self.register_tool(password_analysis_tool)

        # 文本密码生成工具
        text_generation_tool = MCPTool(
            name="generate_password_from_text",
            description="基于文本描述生成密码",
            input_schema={
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "密码描述"},
                    "length": {
                        "type": "integer",
                        "description": "密码长度",
                        "default": 12,
                    },
                    "include_special": {
                        "type": "boolean",
                        "description": "包含特殊字符",
                        "default": True,
                    },
                },
                "required": ["description"],
            },
            handler=None,
        )
        self.register_tool(text_generation_tool)

        # 图像密码分析工具
        image_analysis_tool = MCPTool(
            name="analyze_image_for_password",
            description="基于图像内容生成密码建议",
            input_schema={
                "type": "object",
                "properties": {
                    "image_data": {"type": "string", "description": "Base64图像数据"},
                    "prompt": {
                        "type": "string",
                        "description": "额外提示",
                        "default": "",
                    },
                },
                "required": ["image_data"],
            },
            handler=None,
        )
        self.register_tool(image_analysis_tool)

        # 位置密码生成工具
        location_tool = MCPTool(
            name="generate_location_password",
            description="基于地理位置生成密码",
            input_schema={
                "type": "object",
                "properties": {
                    "locations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "lat": {"type": "number"},
                                "lng": {"type": "number"},
                                "address": {"type": "string"},
                            },
                        },
                        "description": "位置列表",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "额外提示",
                        "default": "",
                    },
                },
                "required": ["locations"],
            },
            handler=None,
        )
        self.register_tool(location_tool)

        # 意图分类工具
        intent_tool = MCPTool(
            name="classify_intent",
            description="分类用户意图",
            input_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "用户消息"}
                },
                "required": ["message"],
            },
            handler=None,
        )
        self.register_tool(intent_tool)

        # 批量分析工具
        batch_tool = MCPTool(
            name="batch_analyze_passwords",
            description="批量分析密码",
            input_schema={
                "type": "object",
                "properties": {
                    "passwords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "密码列表",
                    }
                },
                "required": ["passwords"],
            },
            handler=None,
        )
        self.register_tool(batch_tool)


# 全局工具注册表实例
tool_registry = MCPToolRegistry()
