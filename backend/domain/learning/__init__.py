"""
学习领域 (Learning Domain)

包含学习记录实体定义和仓储接口。
"""

from domain.learning.entity import LearningRecord, KnowledgeCollection
from domain.learning.repository import LearningRepository

__all__ = ["LearningRecord", "KnowledgeCollection", "LearningRepository"]
