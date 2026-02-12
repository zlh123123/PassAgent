from pydantic import BaseModel


# back -> front: 通用操作结果
class MessageResponse(BaseModel):
    message: str
