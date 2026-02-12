from pydantic import BaseModel, EmailStr
from typing import Optional


# back -> front: 获取用户资料
class ProfileResponse(BaseModel):
    user_id: str
    email: str
    nickname: Optional[str] = None
    theme: str = "light"


# front -> back: 更新用户资料
class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = None
    theme: Optional[str] = None
