"""
知识点仓储接口 (KnowledgeRepository Interface)

定义知识库数据访问的抽象接口。
实现在基础设施层。
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.knowledge.entity import KnowledgePoint, KnowledgeSearchResult, ImportResult


class KnowledgeRepository(ABC):
    """
    知识点仓储接口

    定义知识库数据访问的抽象接口，包括初始化、导入、检索等功能。
    """

    @abstractmethod
    async def init_schema(self) -> None:
        """
        初始化数据库模式（首次启动时调用）

        创建必要的表结构、索引等。
        """
        pass

    @abstractmethod
    async def exists(self, knowledge_id: str) -> bool:
        """
        检查知识点是否存在

        Args:
            knowledge_id: 知识点ID

        Returns:
            bool: 是否存在
        """
        pass

    @abstractmethod
    async def save(self, knowledge_point: KnowledgePoint) -> bool:
        """
        保存单个知识点

        Args:
            knowledge_point: 知识点实体

        Returns:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    async def load_all(self, knowledge_points: List[KnowledgePoint]) -> ImportResult:
        """
        批量导入知识点

        Args:
            knowledge_points: 知识点列表

        Returns:
            ImportResult: 导入结果
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        course: Optional[str] = None,
        limit: int = 5
    ) -> List[KnowledgeSearchResult]:
        """
        语义检索知识点

        Args:
            query: 查询文本
            course: 课程过滤条件
            limit: 返回数量限制

        Returns:
            List[KnowledgeSearchResult]: 检索结果列表
        """
        pass

    @abstractmethod
    async def get_by_id(self, knowledge_id: str) -> Optional[KnowledgePoint]:
        """
        根据ID获取知识点

        Args:
            knowledge_id: 知识点ID

        Returns:
            Optional[KnowledgePoint]: 知识点实体，不存在则返回None
        """
        pass

    @abstractmethod
    async def get_by_ids(self, knowledge_ids: List[str]) -> List[KnowledgePoint]:
        """
        根据ID列表批量获取知识点

        Args:
            knowledge_ids: 知识点ID列表

        Returns:
            List[KnowledgePoint]: 知识点列表
        """
        pass

    @abstractmethod
    async def get_by_course(self, course: str) -> List[KnowledgePoint]:
        """
        根据课程获取知识点列表

        Args:
            course: 课程名称

        Returns:
            List[KnowledgePoint]: 知识点列表
        """
        pass

    @abstractmethod
    async def get_prerequisites(self, knowledge_id: str) -> List[KnowledgePoint]:
        """
        获取知识点的前置知识点

        Args:
            knowledge_id: 知识点ID

        Returns:
            List[KnowledgePoint]: 前置知识点列表
        """
        pass

    @abstractmethod
    async def get_successors(self, knowledge_id: str) -> List[KnowledgePoint]:
        """
        获取知识点的后置知识点

        Args:
            knowledge_id: 知识点ID

        Returns:
            List[KnowledgePoint]: 后置知识点列表
        """
        pass

    @abstractmethod
    async def get_related(self, knowledge_id: str) -> List[KnowledgePoint]:
        """
        获取知识点的相关知识点

        Args:
            knowledge_id: 知识点ID

        Returns:
            List[KnowledgePoint]: 相关知识点列表
        """
        pass

    @abstractmethod
    async def update(self, knowledge_point: KnowledgePoint) -> bool:
        """
        更新知识点

        Args:
            knowledge_point: 知识点实体

        Returns:
            bool: 是否更新成功
        """
        pass

    @abstractmethod
    async def delete(self, knowledge_id: str) -> bool:
        """
        删除知识点

        Args:
            knowledge_id: 知识点ID

        Returns:
            bool: 是否删除成功
        """
        pass

    @abstractmethod
    async def count(self) -> int:
        """
        获取知识点总数

        Returns:
            int: 知识点数量
        """
        pass

    @abstractmethod
    async def get_courses(self) -> List[str]:
        """
        获取所有课程名称

        Returns:
            List[str]: 课程名称列表
        """
        pass
