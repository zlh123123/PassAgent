from pydantic import BaseModel
from typing import Optional, List, Any


# front -> back: 提交反馈
class RenameSessionRequest(BaseModel):
    title: str


class FeedbackRequest(BaseModel):
    feedback_type: str


# back -> front: 消息内嵌的反馈信息
class FeedbackInfo(BaseModel):
    feedback_type: str


# back -> front: 单条消息详情
class MessageResponse(BaseModel):
    message_id: str
    content: str
    message_type: str
    created_at: str
    feedback: Optional[FeedbackInfo] = None
    agent_steps: Optional[List[Any]] = None


# back -> front: 单个会话概要
class SessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: str
    updated_at: Optional[str] = None


# back -> front: 会话列表
class SessionsListResponse(BaseModel):
    sessions: List[SessionResponse]


# back -> front: 消息列表
class MessagesListResponse(BaseModel):
    messages: List[MessageResponse]
