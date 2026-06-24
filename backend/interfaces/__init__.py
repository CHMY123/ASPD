"""
接口层 (Interfaces Layer)

处理HTTP请求和响应。
"""

from interfaces.api import chat_router, knowledge_router, learning_router
from interfaces.schemas import (
    ChatRequest,
    ChatResponse,
    KnowledgeImportRequest,
    KnowledgeSearchRequest,
    LearningRecordRequest,
)

__all__ = [
    "chat_router",
    "knowledge_router",
    "learning_router",
    "ChatRequest",
    "ChatResponse",
    "KnowledgeImportRequest",
    "KnowledgeSearchRequest",
    "LearningRecordRequest",
]
