from typing import List, Literal, Optional

from pydantic import BaseModel


MemoryType = Literal["PREFERENCE", "FACT", "CONSTRAINT"]
MemorySource = Literal["MANUAL", "AUTO"]
MemoryClearScope = Literal["all", "manual", "auto"]


class MemorySectionResponse(BaseModel):
    memory_type: MemoryType
    label: str
    items: List[str]


class MemoryProfileResponse(BaseModel):
    content_md: str
    manual_sections: List[MemorySectionResponse]
    auto_sections: List[MemorySectionResponse]
    created_at: str
    updated_at: str
    last_used_at: Optional[str] = None


class SaveMemoryProfileRequest(BaseModel):
    content_md: str


class SaveMemoryProfileResponse(BaseModel):
    message: str


class MemoryItemRequest(BaseModel):
    content: str
    memory_type: MemoryType
    source: MemorySource = "MANUAL"


class UpdateMemoryItemRequest(BaseModel):
    old_content: str
    new_content: str
    memory_type: MemoryType
    source: MemorySource = "MANUAL"


class PromoteMemoryItemRequest(BaseModel):
    content: str
    memory_type: MemoryType


class MemoryOperationResponse(BaseModel):
    message: str
