"""
会话领域 (Conversation Domain)

包含会话和消息实体定义，以及仓储接口。
"""

from domain.conversation.entity import Conversation, Message
from domain.conversation.repository import ConversationRepository

__all__ = ["Conversation", "Message", "ConversationRepository"]
