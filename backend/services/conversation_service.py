"""
Conversation Service for PassAgent
"""

from typing import Dict, Optional
from app.models.api_models import Conversation
import logging

logger = logging.getLogger(__name__)


class ConversationService:
    """会话服务"""

    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}

    def get_or_create_conversation(
        self, conversation_id: Optional[str] = None
    ) -> Conversation:
        """获取或创建会话"""
        if conversation_id and conversation_id in self.conversations:
            return self.conversations[conversation_id]

        # 创建新会话
        conversation = Conversation(conversation_id)
        self.conversations[conversation.id] = conversation
        logger.info(f"创建新会话: {conversation.id}")

        return conversation

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """获取会话"""
        return self.conversations.get(conversation_id)

    def delete_conversation(self, conversation_id: str) -> bool:
        """删除会话"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"删除会话: {conversation_id}")
            return True
        return False


# 全局会话服务实例
conversation_service = ConversationService()
