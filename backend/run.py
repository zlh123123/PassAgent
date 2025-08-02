# backend/run.py
"""
PassAgent 后端启动脚本
"""
import uvicorn
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 启动 PassAgent 后端服务...")
    print("📡 服务地址: http://localhost:8080")
    print("📖 API文档: http://localhost:8080/docs")
    print("🔄 自动重载: 已启用")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
        access_log=True
    )