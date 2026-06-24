"""
学习记录实体 (Learning Entities)

定义用户学习行为的数据结构。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid


class ActionType:
    """操作类型常量"""
    VIEW = "view"
    SEARCH = "search"
    COLLECT = "collect"
    ASK = "ask"
    BROWSE = "browse"
    REVIEW = "review"


@dataclass
class LearningRecord:
    """
    学习记录实体

    Attributes:
        id: 记录唯一标识符
        user_id: 用户ID
        knowledge_point_id: 访问的知识点ID
        action: 操作类型（view/search/collect/ask）
        duration: 停留时长（秒）
        created_at: 操作时间
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    knowledge_point_id: str = ""
    action: str = ""
    duration: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 字典表示
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "knowledge_point_id": self.knowledge_point_id,
            "action": self.action,
            "duration": self.duration,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def create(
        cls,
        user_id: str,
        knowledge_point_id: str,
        action: str,
        duration: int = 0
    ) -> "LearningRecord":
        """
        创建学习记录

        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            action: 操作类型
            duration: 停留时长

        Returns:
            LearningRecord: 学习记录实例
        """
        return cls(
            user_id=user_id,
            knowledge_point_id=knowledge_point_id,
            action=action,
            duration=duration,
        )


@dataclass
class KnowledgeCollection:
    """
    知识收藏实体

    Attributes:
        id: 收藏唯一标识符
        user_id: 用户ID
        knowledge_point_id: 知识点ID
        folder: 收藏夹名称
        created_at: 收藏时间
        note: 用户备注
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    knowledge_point_id: str = ""
    folder: str = "默认收藏夹"
    created_at: datetime = field(default_factory=datetime.now)
    note: str = ""

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 字典表示
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "knowledge_point_id": self.knowledge_point_id,
            "folder": self.folder,
            "created_at": self.created_at.isoformat(),
            "note": self.note,
        }

    @classmethod
    def create(
        cls,
        user_id: str,
        knowledge_point_id: str,
        folder: str = "默认收藏夹",
        note: str = ""
    ) -> "KnowledgeCollection":
        """
        创建知识收藏

        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            folder: 收藏夹名称
            note: 用户备注

        Returns:
            KnowledgeCollection: 收藏实例
        """
        return cls(
            user_id=user_id,
            knowledge_point_id=knowledge_point_id,
            folder=folder,
            note=note,
        )


@dataclass
class LearningStats:
    """
    学习统计

    Attributes:
        user_id: 用户ID
        total_views: 总浏览次数
        total_searches: 总搜索次数
        total_questions: 总提问次数
        total_collections: 总收藏数
        total_duration: 总学习时长（秒）
        knowledge_coverage: 知识点覆盖率
        recent_activities: 最近活动列表
    """
    user_id: str
    total_views: int = 0
    total_searches: int = 0
    total_questions: int = 0
    total_collections: int = 0
    total_duration: int = 0
    knowledge_coverage: float = 0.0
    recent_activities: List[LearningRecord] = field(default_factory=list)

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 字典表示
        """
        return {
            "user_id": self.user_id,
            "total_views": self.total_views,
            "total_searches": self.total_searches,
            "total_questions": self.total_questions,
            "total_collections": self.total_collections,
            "total_duration": self.total_duration,
            "knowledge_coverage": self.knowledge_coverage,
            "recent_activities": [a.to_dict() for a in self.recent_activities],
        }
