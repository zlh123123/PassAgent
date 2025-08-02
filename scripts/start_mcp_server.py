#!/usr/bin/env python3
"""
启动PassAgent MCP服务器
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.mcp.server import PassAgentMCPServer
from backend.app.core.config import settings


async def main():
    """启动MCP服务器"""
    print("🚀 启动PassAgent MCP服务器...")

    server = PassAgentMCPServer()

    try:
        await server.run(host=settings.mcp_server_host, port=settings.mcp_server_port)
    except KeyboardInterrupt:
        print("\n🛑 MCP服务器已停止")
    except Exception as e:
        print(f"❌ MCP服务器启动失败: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
