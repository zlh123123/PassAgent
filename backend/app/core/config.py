# backend/app/core/config.py
"""
PassAgent Backend Configuration
"""
import os
import secrets
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""

    # Application
    app_name: str = Field(default="PassAgent", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=True, env="DEBUG")  # 开发模式默认为True
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8080, env="PORT")

    # Database
    database_url: str = Field(default="sqlite:///./passagent.db", env="DATABASE_URL")

    # Security - 为开发提供默认值
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY"
    )
    access_token_expire_minutes: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    algorithm: str = Field(default="HS256", env="ALGORITHM")

    # AI Models - 都设为可选
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")

    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(
        default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL"
    )

    qwen_api_key: Optional[str] = Field(default=None, env="QWEN_API_KEY")
    qwen_model: str = Field(default="qwen-max", env="QWEN_MODEL")

    deepseek_api_key: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    deepseek_model: str = Field(default="deepseek-chat", env="DEEPSEEK_MODEL")

    # MCP Server
    mcp_server_url: str = Field(default="http://localhost:8081", env="MCP_SERVER_URL")
    mcp_server_port: int = Field(default=8081, env="MCP_SERVER_PORT")
    mcp_server_host: str = Field(default="localhost", env="MCP_SERVER_HOST")
    mcp_enabled: bool = Field(default=True, env="MCP_ENABLED")
    mcp_timeout: int = Field(default=30, env="MCP_TIMEOUT")

    # Redis - 设为可选
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")

    # Password Analysis
    pwned_passwords_api_url: str = Field(
        default="https://api.pwnedpasswords.com/range/", env="PWNED_PASSWORDS_API_URL"
    )
    hashcat_rules_path: str = Field(default="./rules/", env="HASHCAT_RULES_PATH")
    wordlist_path: str = Field(default="./wordlists/", env="WORDLIST_PATH")

    # File Upload
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_image_extensions: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
        env="ALLOWED_IMAGE_EXTENSIONS",
    )
    allowed_audio_extensions: List[str] = Field(
        default=[".mp3", ".wav", ".ogg", ".m4a", ".flac"],
        env="ALLOWED_AUDIO_EXTENSIONS",
    )

    # CORS
    allowed_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
        ],
        env="ALLOWED_ORIGINS",
    )
    allowed_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"], env="ALLOWED_METHODS"
    )
    allowed_headers: List[str] = Field(default=["*"], env="ALLOWED_HEADERS")

    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/passagent.log", env="LOG_FILE")

    # Vector Database (Optional)
    milvus_host: str = Field(default="localhost", env="MILVUS_HOST")
    milvus_port: int = Field(default=19530, env="MILVUS_PORT")
    milvus_database: str = Field(default="passagent", env="MILVUS_DATABASE")

    # Geographic Services
    geocoding_api_key: Optional[str] = Field(default=None, env="GEOCODING_API_KEY")

    # Encryption
    encryption_key: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
