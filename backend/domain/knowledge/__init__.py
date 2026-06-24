"""
知识点领域 (Knowledge Domain)

包含知识点实体定义和仓储接口。
"""

from domain.knowledge.entity import KnowledgePoint
from domain.knowledge.repository import KnowledgeRepository

__all__ = ["KnowledgePoint", "KnowledgeRepository"]
