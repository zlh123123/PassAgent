# backend/app/api/v1/upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Optional
import os
import uuid
import base64
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg", "audio/mp4"}

@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    """上传图片文件"""
    try:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的图片格式: {file.content_type}"
            )
        
        # 生成唯一文件名
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 转换为base64用于AI分析
        base64_data = base64.b64encode(content).decode('utf-8')
        
        return {
            "filename": unique_filename,
            "file_path": str(file_path),
            "file_url": f"/uploads/{unique_filename}",
            "file_size": len(content),
            "content_type": file.content_type,
            "base64_data": f"data:{file.content_type};base64,{base64_data}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片上传失败: {str(e)}")

@router.post("/audio")
async def upload_audio(file: UploadFile = File(...)):
    """上传音频文件"""
    try:
        if file.content_type not in ALLOWED_AUDIO_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的音频格式: {file.content_type}"
            )
        
        # 生成唯一文件名
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        return {
            "filename": unique_filename,
            "file_path": str(file_path),
            "file_url": f"/uploads/{unique_filename}",
            "file_size": len(content),
            "content_type": file.content_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音频上传失败: {str(e)}")

@router.delete("/file/{filename}")
async def delete_file(filename: str):
    """删除上传的文件"""
    try:
        file_path = UPLOAD_DIR / filename
        if file_path.exists():
            os.remove(file_path)
            return {"message": f"文件 {filename} 删除成功"}
        else:
            raise HTTPException(status_code=404, detail="文件不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")