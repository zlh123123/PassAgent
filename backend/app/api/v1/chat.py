# backend/app/api/v1/chat.py
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import logging
import re

from app.models.api_models import ChatMessage, ChatRequest, ChatResponse, Message
from app.services.ai_service import AIService
from app.services.conversation_service import conversation_service
from app.mcp.client import mcp_client

router = APIRouter()
logger = logging.getLogger(__name__)
ai_service = AIService()


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """发送聊天消息 - 集成MCP工具调用"""
    try:
        # 获取或创建会话
        conversation = conversation_service.get_or_create_conversation(
            request.conversation_id
        )

        # 添加用户消息
        user_message = Message(
            role="user",
            content=request.content,
            message_type=request.message_type or "text",
            metadata=request.metadata or {},
        )
        conversation.messages.append(user_message)

        # 智能工具选择和调用
        response_content = await _generate_intelligent_response(request, conversation)

        # 添加助手回复
        assistant_message = Message(
            role="assistant", content=response_content, message_type="text"
        )
        conversation.messages.append(assistant_message)

        return ChatResponse(
            message=response_content,
            conversation_id=conversation.id,
            message_id=assistant_message.id,
            suggestions=ai_service.get_follow_up_suggestions(request.content),
        )

    except Exception as e:
        logger.error(f"聊天处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"消息处理失败: {str(e)}")


async def _generate_intelligent_response(request: ChatRequest, conversation) -> str:
    """生成智能响应 - 根据内容类型和意图调用不同工具"""

    # 多模态内容直接导向密码推荐
    if request.message_type == "image" and request.metadata.get("image_data"):
        return await _handle_image_password_generation(request)

    elif request.message_type == "location" and request.metadata.get("locations"):
        return await _handle_location_password_generation(request)

    elif request.message_type == "audio" and request.metadata.get("audio_data"):
        return await _handle_audio_password_generation(request)

    # 纯文本需要进行意图分类
    else:
        return await _handle_text_message_with_intent(request, conversation)


async def _handle_image_password_generation(request: ChatRequest) -> str:
    """处理图像密码生成"""
    try:
        async with mcp_client:
            return await mcp_client.generate_smart_password(
                "image",
                image_data=request.metadata["image_data"],
                prompt=request.content,
            )
    except Exception as e:
        logger.error(f"图像密码生成失败: {str(e)}")
        return await ai_service.analyze_image_for_password(
            request.metadata["image_data"], request.content
        )


async def _handle_location_password_generation(request: ChatRequest) -> str:
    """处理位置密码生成"""
    try:
        async with mcp_client:
            return await mcp_client.generate_smart_password(
                "location",
                locations=request.metadata["locations"],
                prompt=request.content,
            )
    except Exception as e:
        logger.error(f"位置密码生成失败: {str(e)}")
        return await ai_service.generate_location_based_password(
            request.metadata["locations"], request.content
        )


async def _handle_audio_password_generation(request: ChatRequest) -> str:
    """处理音频密码生成"""
    # 音频需要先转文本，然后基于文本生成密码
    try:
        # 这里可以集成语音识别服务
        # 暂时返回基于文本的密码生成
        return await ai_service.generate_text_response(
            f"基于音频内容生成密码建议: {request.content}"
        )
    except Exception as e:
        logger.error(f"音频密码生成失败: {str(e)}")
        return "音频密码生成功能正在开发中，请使用文本或图片方式。"


async def _handle_text_message_with_intent(request: ChatRequest, conversation) -> str:
    """处理文本消息 - 需要意图分类"""
    try:
        # 使用MCP进行意图分类
        async with mcp_client:
            intent_result = await mcp_client.classify_user_intent(request.content)

        intent = intent_result.get("intent", "general_chat")
        confidence = intent_result.get("confidence", 0.0)

        logger.info(f"用户意图分类: {intent} (置信度: {confidence})")

        # 根据意图调用不同的处理函数
        if intent == "password_analysis":
            return await _handle_password_analysis_intent(request)

        elif intent == "password_generation":
            return await _handle_password_generation_intent(request)

        elif intent == "leak_check":
            return await _handle_leak_check_intent(request)

        else:
            # 普通对话
            return await ai_service.generate_text_response(
                request.content,
                conversation.messages[-5:] if len(conversation.messages) > 5 else [],
            )

    except Exception as e:
        logger.error(f"意图分类失败，降级到普通对话: {str(e)}")
        return await ai_service.generate_text_response(
            request.content,
            conversation.messages[-5:] if len(conversation.messages) > 5 else [],
        )


async def _handle_password_analysis_intent(request: ChatRequest) -> str:
    """处理密码分析意图"""
    password = _extract_password_from_content(request.content)
    if password:
        try:
            async with mcp_client:
                analysis = await mcp_client.analyze_password_with_tools(password)
                return _format_password_analysis(analysis)
        except Exception as e:
            logger.error(f"MCP密码分析失败: {str(e)}")
            return await ai_service.analyze_password_with_ai(password)
    else:
        return "请提供要分析的密码。您可以用引号包围密码，例如：分析密码'Password123!'"


async def _handle_password_generation_intent(request: ChatRequest) -> str:
    """处理密码生成意图"""
    try:
        async with mcp_client:
            return await mcp_client.generate_smart_password(
                "text",
                description=request.content,
                length=12,
                include_special=True,
            )
    except Exception as e:
        logger.error(f"MCP密码生成失败: {str(e)}")
        return await ai_service.generate_text_response(request.content)


async def _handle_leak_check_intent(request: ChatRequest) -> str:
    """处理泄露检查意图"""
    password = _extract_password_from_content(request.content)
    if password:
        try:
            async with mcp_client:
                analysis = await mcp_client.analyze_password_with_tools(password)
                leak_info = analysis.get("leak", {})

                if leak_info.get("is_leaked"):
                    return f"⚠️ **安全警告**: 密码已在 {leak_info.get('leak_count', 0)} 次数据泄露中发现\n\n建议立即更换此密码！"
                else:
                    return "✅ **安全检查**: 未发现此密码在已知泄露数据库中，但仍建议定期更换密码。"
        except Exception as e:
            logger.error(f"泄露检查失败: {str(e)}")
            return "泄露检查服务暂时不可用，请稍后再试。"
    else:
        return "请提供要检查的密码。您可以用引号包围密码，例如：检查密码'Password123!'是否泄露"


def _extract_password_from_content(content: str) -> Optional[str]:
    """从聊天内容中提取密码"""
    patterns = [
        r"'([^']+)'",
        r'"([^"]+)"',
        r"密码[是为]?\s*[:：]\s*(\S+)",
        r"password\s*[:：]\s*(\S+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def _format_password_analysis(analysis: Dict[str, Any]) -> str:
    """格式化密码分析结果"""
    if "error" in analysis:
        return f"密码分析遇到问题: {analysis['error']}"

    result = ["🔐 **密码安全分析报告**\n"]

    if "strength" in analysis:
        strength = analysis["strength"]
        result.append(f"**强度评分**: {strength.get('score', 0)}/100")
        result.append(f"**安全等级**: {strength.get('level', '未知')}")
        result.append(
            f"**密码长度**: {len(strength.get('password', ''))if 'password' in strength else 0} 字符"
        )

        if strength.get("suggestions"):
            result.append("\n📝 **改进建议**:")
            for suggestion in strength["suggestions"]:
                result.append(f"• {suggestion}")

    if "leak" in analysis:
        leak = analysis["leak"]
        if leak.get("is_leaked"):
            result.append(
                f"\n⚠️ **安全警告**: 此密码已在 {leak.get('leak_count', 0)} 次数据泄露中发现"
            )
            result.append(f"**风险等级**: {leak.get('risk_level', '未知')}")
        else:
            result.append("\n✅ **泄露检查**: 未发现在已知泄露数据库中")

    return "\n".join(result)


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """获取会话历史"""
    conversation = conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")

    return {
        "conversation_id": conversation.id,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "message_type": msg.message_type,
                "timestamp": msg.timestamp.isoformat(),
            }
            for msg in conversation.messages
        ],
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """删除会话"""
    success = conversation_service.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")

    return {"message": "会话已删除"}
