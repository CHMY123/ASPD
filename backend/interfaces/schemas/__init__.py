"""
Pydantic Schema层
"""

from interfaces.schemas.chat_schema import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
)
from interfaces.schemas.knowledge_schema import (
    KnowledgePointResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    KnowledgeImportRequest,
    KnowledgeImportResponse,
    KnowledgeDetailResponse,
)
from interfaces.schemas.learning_schema import (
    LearningRecordRequest,
    LearningRecordResponse,
    LearningStatsResponse,
    CollectionRequest,
    CollectionResponse,
)

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "ConversationResponse",
    "KnowledgePointResponse",
    "KnowledgeSearchRequest",
    "KnowledgeSearchResponse",
    "KnowledgeImportRequest",
    "KnowledgeImportResponse",
    "KnowledgeDetailResponse",
    "LearningRecordRequest",
    "LearningRecordResponse",
    "LearningStatsResponse",
    "CollectionRequest",
    "CollectionResponse",
]
