from pydantic import BaseModel
from typing import List, Optional


# back -> front: 单条记忆详情
class MemoryResponse(BaseModel):
    memory_id: str
    content: str
    memory_type: str
    source: str
    created_at: str


# front -> back: 创建记忆
class CreateMemoryRequest(BaseModel):
    content: str
    memory_type: str


# back -> front: 创建记忆结果
class CreateMemoryResponse(BaseModel):
    memory_id: str
    message: str


# back -> front: 记忆列表
class MemoriesListResponse(BaseModel):
    memories: List[MemoryResponse]
