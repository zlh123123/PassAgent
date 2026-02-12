"""FastAPI 入口，挂载路由，启动 worker 协程"""
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

from database.init_db import init_database
from routers import auth, user, session, chat, upload, feedback, memory
from worker.runner import worker_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    init_database()
    os.makedirs("uploads", exist_ok=True)
    # 启动 worker 协程
    worker_task = asyncio.create_task(worker_loop())
    yield
    worker_task.cancel()


app = FastAPI(
    title="PassAgent API",
    description="PassAgent - 基于大语言模型的个人全能口令助手",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(session.router)
app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(feedback.router)
app.include_router(memory.router)


@app.get("/")
async def root():
    return {"message": "PassAgent API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
