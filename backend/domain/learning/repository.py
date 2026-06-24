"""
学习仓储接口 (LearningRepository Interface)

定义学习记录数据访问的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.learning.entity import LearningRecord, KnowledgeCollection, LearningStats


class LearningRepository(ABC):
    """
    学习仓储接口

    定义学习记录和知识收藏数据访问的抽象接口。
    """

    @abstractmethod
    async def init_schema(self) -> None:
        """
        初始化数据库模式
        """
        pass

    @abstractmethod
    async def add_record(self, record: LearningRecord) -> bool:
        """
        添加学习记录

        Args:
            record: 学习记录实体

        Returns:
            bool: 是否添加成功
        """
        pass

    @abstractmethod
    async def get_records_by_user(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[LearningRecord]:
        """
        获取用户的学习记录

        Args:
            user_id: 用户ID
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            List[LearningRecord]: 学习记录列表
        """
        pass

    @abstractmethod
    async def get_records_by_knowledge(
        self,
        knowledge_point_id: str,
        limit: int = 50
    ) -> List[LearningRecord]:
        """
        获取知识点的所有学习记录

        Args:
            knowledge_point_id: 知识点ID
            limit: 返回数量限制

        Returns:
            List[LearningRecord]: 学习记录列表
        """
        pass

    @abstractmethod
    async def get_user_stats(self, user_id: str) -> LearningStats:
        """
        获取用户学习统计

        Args:
            user_id: 用户ID

        Returns:
            LearningStats: 学习统计
        """
        pass

    @abstractmethod
    async def add_collection(self, collection: KnowledgeCollection) -> bool:
        """
        添加知识收藏

        Args:
            collection: 收藏实体

        Returns:
            bool: 是否添加成功
        """
        pass

    @abstractmethod
    async def remove_collection(
        self,
        user_id: str,
        knowledge_point_id: str
    ) -> bool:
        """
        取消收藏

        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID

        Returns:
            bool: 是否取消成功
        """
        pass

    @abstractmethod
    async def get_collections_by_user(
        self,
        user_id: str,
        folder: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[KnowledgeCollection]:
        """
        获取用户的收藏列表

        Args:
            user_id: 用户ID
            folder: 收藏夹名称过滤
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            List[KnowledgeCollection]: 收藏列表
        """
        pass

    @abstractmethod
    async def is_collected(
        self,
        user_id: str,
        knowledge_point_id: str
    ) -> bool:
        """
        检查是否已收藏

        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID

        Returns:
            bool: 是否已收藏
        """
        pass

    @abstractmethod
    async def get_user_folders(self, user_id: str) -> List[str]:
        """
        获取用户的收藏夹列表

        Args:
            user_id: 用户ID

        Returns:
            List[str]: 收藏夹名称列表
        """
        pass

    @abstractmethod
    async def create_folder(self, user_id: str, folder_name: str) -> bool:
        """
        创建收藏夹

        Args:
            user_id: 用户ID
            folder_name: 收藏夹名称

        Returns:
            bool: 是否创建成功
        """
        pass

    @abstractmethod
    async def delete_folder(self, user_id: str, folder_name: str) -> bool:
        """
        删除收藏夹

        Args:
            user_id: 用户ID
            folder_name: 收藏夹名称

        Returns:
            bool: 是否删除成功
        """
        pass

    @abstractmethod
    async def get_recent_learning_path(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[str]:
        """
        获取用户最近的学习路径（知识点ID列表）

        Args:
            user_id: 用户ID
            limit: 返回数量限制

        Returns:
            List[str]: 知识点ID列表
        """
        pass
