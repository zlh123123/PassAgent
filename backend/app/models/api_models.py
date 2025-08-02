# backend/app/models/api_models.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class PasswordAnalysisRequest(BaseModel):
    password: str
    analysis_types: List[str] = ["strength", "leak"]
    include_suggestions: bool = True


class PasswordAnalysisResponse(BaseModel):
    password_length: int
    strength_score: int
    strength_level: str
    is_leaked: Optional[bool]
    leak_count: int
    risk_level: str
    suggestions: List[str]
    analysis_details: Dict[str, Any]
    breach_sources: List[str]


class ChatRequest(BaseModel):
    content: str
    message_type: str = "text"
    context: Optional[List[Dict]] = None
    image_data: Optional[str] = None
    location_data: Optional[List[Dict]] = None
    metadata: Optional[Dict] = None


class ChatResponse(BaseModel):
    message: str
    message_type: str = "assistant"
    suggestions: List[str] = []
    metadata: Dict[str, Any] = {}


class PasswordBatchRequest(BaseModel):
    passwords: List[str]


class PasswordStrengthResult(BaseModel):
    password: str
    strength_score: int
    strength_level: str
    is_leaked: Optional[bool]
    leak_count: int
    risk_level: str


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None
