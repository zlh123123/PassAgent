from typing import List, Optional

from pydantic import BaseModel


class MemorySectionResponse(BaseModel):
    memory_type: str
    label: str
    items: List[str]


class MemoryProfileResponse(BaseModel):
    content_md: str
    sections: List[MemorySectionResponse]
    created_at: str
    updated_at: str
    last_used_at: Optional[str] = None


class SaveMemoryProfileRequest(BaseModel):
    content_md: str


class SaveMemoryProfileResponse(BaseModel):
    message: str


class MemoryItemRequest(BaseModel):
    content: str
    memory_type: str


class UpdateMemoryItemRequest(BaseModel):
    old_content: str
    new_content: str
    memory_type: str


class MemoryOperationResponse(BaseModel):
    message: str
