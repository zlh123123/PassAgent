from pydantic import BaseModel
from typing import Optional, Any


class ExportResponse(BaseModel):
    conversations: Optional[Any] = None
    memories: Optional[Any] = None
    settings: Optional[Any] = None
