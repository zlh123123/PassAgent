"""文件存储、类型校验（仅图片/音频）、删除"""
import os
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session as DBSession

from database.models import UploadedFile
from config import UPLOAD_DIR

ALLOWED_TYPES = {
    "image/png", "image/jpeg", "image/webp",
    "audio/wav", "audio/mpeg", "audio/flac",
}


def validate_file_type(content_type: str) -> bool:
    return content_type in ALLOWED_TYPES


def save_file(
    db: DBSession,
    user_id: str,
    filename: str,
    content_type: str,
    file_data: bytes,
    session_id: str | None = None,
) -> dict:
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(filename)[1] or ""
    stored_name = f"{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, stored_name)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file_data)

    record = UploadedFile(
        file_id=file_id,
        user_id=user_id,
        session_id=session_id,
        filename=filename,
        file_path=file_path,
        file_size=len(file_data),
        file_type=content_type,
        uploaded_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(record)
    db.commit()

    return {
        "file_id": file_id,
        "filename": filename,
        "file_type": content_type,
        "file_size": len(file_data),
    }


def list_files(db: DBSession, user_id: str) -> list[dict]:
    files = (
        db.query(UploadedFile)
        .filter(UploadedFile.user_id == user_id)
        .order_by(UploadedFile.uploaded_at.desc())
        .all()
    )
    return [
        {
            "file_id": f.file_id,
            "filename": f.filename,
            "file_type": f.file_type,
            "file_size": f.file_size,
            "session_id": f.session_id,
            "uploaded_at": f.uploaded_at,
        }
        for f in files
    ]


def delete_file(db: DBSession, user_id: str, file_id: str) -> bool:
    record = (
        db.query(UploadedFile)
        .filter(UploadedFile.file_id == file_id, UploadedFile.user_id == user_id)
        .first()
    )
    if not record:
        return False
    if os.path.exists(record.file_path):
        os.remove(record.file_path)
    db.delete(record)
    db.commit()
    return True
