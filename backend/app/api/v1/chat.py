# backend/app/api/v1/chat.py
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import asyncio

from app.models.api_models import ChatMessage, ChatRequest, ChatResponse
from app.services.ai_service import AIService

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """发送聊天消息并获取AI回复"""
    try:
        ai_service = AIService()
        
        # 根据消息类型处理
        if request.message_type == "text":
            response = await ai_service.generate_text_response(
                message=request.content,
                context=request.context or []
            )
        
        elif request.message_type == "password_analysis":
            response = await ai_service.analyze_password_with_ai(
                password=request.content,
                analysis_context=request.metadata
            )
        
        elif request.message_type == "image":
            response = await ai_service.analyze_image_for_password(
                image_data=request.image_data,
                prompt=request.content
            )
        
        elif request.message_type == "location":
            response = await ai_service.generate_location_based_password(
                locations=request.location_data,
                prompt=request.content
            )
        
        else:
            response = await ai_service.generate_text_response(
                message=request.content,
                context=request.context or []
            )
        
        return ChatResponse(
            message=response,
            message_type="assistant",
            suggestions=ai_service.get_follow_up_suggestions(request.content),
            metadata={"response_time": "1.2s", "model": "gpt-3.5-turbo"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聊天处理失败: {str(e)}")

@router.post("/analyze-image")
async def analyze_image_for_password(request: Dict[str, Any]):
    """分析图片内容生成密码建议"""
    try:
        ai_service = AIService()
        result = await ai_service.analyze_image_for_password(
            image_data=request.get("image_data"),
            prompt=request.get("prompt", "根据这张图片生成密码建议")
        )
        
        return {"response": result, "type": "image_analysis"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片分析失败: {str(e)}")