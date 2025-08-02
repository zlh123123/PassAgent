"""
API Models for PassAgent
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid


class ChatMessage(BaseModel):
    """聊天消息模型"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str = Field(..., description="消息角色: user/assistant")
    content: str = Field(..., description="消息内容")
    message_type: str = Field(
        default="text", description="消息类型: text/image/audio/location"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="附加元数据")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """聊天请求模型"""

    content: str = Field(..., description="用户消息内容")
    message_type: Optional[str] = Field(default="text", description="消息类型")
    conversation_id: Optional[str] = Field(default=None, description="会话ID")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="附加数据"
    )


class ChatResponse(BaseModel):
    """聊天响应模型"""

    message: str = Field(..., description="AI回复内容")
    conversation_id: str = Field(..., description="会话ID")
    message_id: str = Field(..., description="消息ID")
    suggestions: List[str] = Field(default_factory=list, description="后续建议")


class PasswordAnalysisRequest(BaseModel):
    """密码分析请求"""

    password: str = Field(..., description="要分析的密码")
    include_suggestions: bool = Field(default=True, description="是否包含改进建议")


class PasswordAnalysisResponse(BaseModel):
    """密码分析响应"""

    password_length: int
    strength_score: int
    strength_level: str
    is_leaked: Optional[bool]
    leak_count: int
    risk_level: str
    suggestions: List[str]
    analysis_details: Dict[str, Any]
    breach_sources: List[str]


class PasswordBatchRequest(BaseModel):
    """批量密码分析请求"""

    passwords: List[str] = Field(..., description="密码列表")


class PasswordStrengthResult(BaseModel):
    """密码强度结果"""

    password: str
    strength_score: int
    strength_level: str
    is_leaked: Optional[bool]
    leak_count: int
    risk_level: str


# 会话管理
class Conversation:
    """会话管理类"""

    def __init__(self, conversation_id: str = None):
        self.id = conversation_id or str(uuid.uuid4())
        self.messages: List[ChatMessage] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


class Message:
    """消息类"""

    def __init__(
        self, role: str, content: str, message_type: str = "text", metadata: Dict = None
    ):
        self.id = str(uuid.uuid4())
        self.role = role
        self.content = content
        self.message_type = message_type
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
