"""
领域层 (Domain Layer)

包含核心业务实体、值对象和仓储接口定义。
该层不依赖任何外部框架或库，保持纯粹的领域逻辑。
"""

from domain.knowledge.entity import KnowledgePoint
from domain.conversation.entity import Conversation, Message
from domain.learning.entity import LearningRecord
from domain.user.entity import User

__all__ = [
    "KnowledgePoint",
    "Conversation",
    "Message",
    "LearningRecord",
    "User",
]
