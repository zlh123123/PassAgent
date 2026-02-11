"""SQLite 连接管理"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 数据库文件路径
DATABASE_PATH = os.getenv("DATABASE_PATH", "passagent.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 需要
    echo=False,
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """获取数据库会话（FastAPI 依赖注入用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
