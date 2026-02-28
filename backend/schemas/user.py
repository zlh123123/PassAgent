from pydantic import BaseModel
from typing import Optional


# back -> front: 获取用户资料
class ProfileResponse(BaseModel):
    user_id: str
    email: str
    nickname: Optional[str] = None
    theme: str = "system"
    font_size: str = "M"
    bubble_style: str = "rounded"
    gen_auto_mode: int = 1
    gen_security_weight: str = "0.5"


# front -> back: 更新用户资料
class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = None
    theme: Optional[str] = None
    font_size: Optional[str] = None
    bubble_style: Optional[str] = None
    gen_auto_mode: Optional[int] = None
    gen_security_weight: Optional[str] = None


# front -> back: 修改密码
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
