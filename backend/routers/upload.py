"""文件上传路由"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session as DBSession

from database.connection import get_db
from database.models import User
from utils.deps import get_current_user
from schemas.file import UploadResponse, FilesListResponse
from services.file_service import validate_file_type, save_file, list_files, delete_file
from config import MAX_UPLOAD_SIZE

router = APIRouter(prefix="/api", tags=["files"])


@router.post("/upload", response_model=UploadResponse)
async def upload(
    file: UploadFile = File(...),
    session_id: str | None = Form(None),
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    if not file.content_type or not validate_file_type(file.content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持图片(png/jpeg/webp)和音频(wav/mp3/flac)文件",
        )

    data = await file.read()
    if len(data) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小超过 10MB 限制",
        )

    result = save_file(
        db,
        user_id=user.user_id,
        filename=file.filename or "unknown",
        content_type=file.content_type,
        file_data=data,
        session_id=session_id,
    )
    return UploadResponse(**result)


@router.get("/files", response_model=FilesListResponse)
def get_files(
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    files = list_files(db, user.user_id)
    return FilesListResponse(files=files)


@router.delete("/files/{file_id}")
def remove_file(
    file_id: str,
    user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    ok = delete_file(db, user.user_id, file_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
    return {"message": "已删除"}
