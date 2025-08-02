# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os

from app.core.config import settings
from app.api.v1 import password, chat, upload
from app.database.database import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    print("🚀 PassAgent后端启动中...")
    create_tables()
    print("✅ 数据库初始化完成")
    
    yield
    
    # 关闭时清理
    print("🛑 PassAgent后端关闭")

app = FastAPI(
    title="PassAgent API",
    description="PassAgent - 基于大语言模型的个人全能口令助手",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置 - 允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React开发服务器
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 静态文件服务
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 注册API路由
app.include_router(password.router, prefix="/api/v1/password", tags=["password"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["upload"])

@app.get("/")
async def root():
    return {
        "message": "PassAgent API Server",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )