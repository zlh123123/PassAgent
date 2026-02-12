from pydantic import BaseModel
from typing import List


# front -> back: 发送对话消息
class ChatRequest(BaseModel):
    message: str
    file_ids: List[str] = []
