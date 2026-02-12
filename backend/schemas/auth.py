from pydantic import BaseModel, EmailStr
from typing import Optional


# front -> back: 发送验证码
class SendCodeRequest(BaseModel):
    email: EmailStr


# back -> front: 发送验证码结果
class SendCodeResponse(BaseModel):
    message: str
    expires_in: int


# front -> back: 注册
class RegisterRequest(BaseModel):
    email: EmailStr
    code: str
    password: str
    nickname: Optional[str] = None


# back -> front: 注册结果
class RegisterResponse(BaseModel):
    user_id: str
    token: str


# front -> back: 登录
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# back -> front: 登录结果
class LoginResponse(BaseModel):
    user_id: str
    token: str
    nickname: Optional[str] = None
    theme: str = "light"
