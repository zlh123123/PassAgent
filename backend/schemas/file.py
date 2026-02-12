from pydantic import BaseModel
from typing import List, Optional


# back -> front: 上传文件结果
class UploadResponse(BaseModel):
    file_id: str
    filename: str
    file_type: str
    file_size: int


# back -> front: 单个文件详情
class FileResponse(BaseModel):
    file_id: str
    filename: str
    file_type: str
    file_size: int
    session_id: Optional[str] = None
    uploaded_at: str


# back -> front: 文件列表
class FilesListResponse(BaseModel):
    files: List[FileResponse]
