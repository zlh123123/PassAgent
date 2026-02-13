"""环境变量读取、路径常量、JWT 配置"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- 数据库 ---
DATABASE_PATH = os.getenv("DATABASE_PATH", "passagent.db")

# --- JWT ---
JWT_SECRET = os.getenv("JWT_SECRET", "passagent-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "72"))

# --- 邮件验证码 ---
VERIFY_CODE_EXPIRE_SECONDS = 300  # 5 分钟
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@passagent.dev")

# --- 文件上传 ---
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

# --- 模型服务（本地 vLLM） ---
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:6006/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "EMPTY")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen3-4b")
