"""
学习辅助应用服务 (Learning Application Service)

处理学习记录、知识推荐等业务逻辑。
"""

from typing import List, Optional, Dict, Any
from domain.learning.entity import (
    LearningRecord,
    KnowledgeCollection,
    LearningStats,
    ActionType
)
from domain.learning.repository import LearningRepository
from domain.knowledge.entity import KnowledgePoint, KnowledgeSearchResult
from domain.knowledge.repository import KnowledgeRepository


class LearningService:
    """
    学习辅助应用服务

    协调学习记录领域对象和知识库，提供学习辅助相关业务操作。

    Attributes:
        learning_repo: 学习记录仓储接口
        knowledge_repo: 知识库仓储接口
    """

    def __init__(
        self,
        learning_repo: LearningRepository,
        knowledge_repo: KnowledgeRepository
    ):
        """
        初始化学习服务

        Args:
            learning_repo: 学习记录仓储接口
            knowledge_repo: 知识库仓储接口
        """
        self.learning_repo = learning_repo
        self.knowledge_repo = knowledge_repo

    async def initialize(self) -> None:
        """
        初始化学习服务

        初始化数据库模式。
        """
        await self.learning_repo.init_schema()

    async def record_action(
        self,
        user_id: str,
        knowledge_point_id: str,
        action: str,
        duration: int = 0
    ) -> LearningRecord:
        """
        记录用户学习行为

        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            action: 操作类型
            duration: 停留时长

        Returns:
            LearningRecord: 创建的学习记录
        """
        record = LearningRecord.create(
            user_id=user_id,
            knowledge_point_id=knowledge_point_id,
            action=action,
            duration=duration
        )
        await self.learning_repo.add_record(record)
        return record

    async def record_view(
        self,
        user_id: str,
        knowledge_point_id: str,
        duration: int = 0
    ) -> LearningRecord:
        """
        记录浏览行为

        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            duration: 停留时长

        Returns:
            LearningRecord: 创建的学习记录
        """
        return await self.record_action(
            user_id, knowledge_point_id, ActionType.VIEW, duration
        )

    async def record_search(
        self,
        user_id: str,
        knowledge_point_id: str
    ) -> LearningRecord:
        """
        记录搜索行为

        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID

        Returns:
            LearningRecord: 创建的学习记录
        """
        return await self.record_action(
            user_id, knowledge_point_id, ActionType.SEARCH
        )

    async def record_question(
        self,
        user_id: str,
        knowledge_point_id: str
    ) -> LearningRecord:
        """
        记录提问行为

        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID

        Returns:
            LearningRecord: 创建的学习记录
        """
        return await self.record_action(
            user_id, knowledge_point_id, ActionType.ASK
        )

    async def get_user_stats(self, user_id: str) -> LearningStats:
        """
        获取用户学习统计

        Args:
            user_id: 用户ID

        Returns:
            LearningStats: 学习统计
        """
        return await self.learning_repo.get_user_stats(user_id)

    async def get_user_learning_path(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取用户学习路径

        Args:
            user_id: 用户ID
            limit: 返回数量限制

        Returns:
            List[Dict]: 学习路径列表
        """
        knowledge_ids = await self.learning_repo.get_recent_learning_path(
            user_id, limit
        )
        path = []
        for kid in knowledge_ids:
            knowledge = await self.knowledge_repo.get_by_id(kid)
            if knowledge:
                path.append({
                    "id": knowledge.id,
                    "title": knowledge.title,
                    "course": knowledge.course,
                })
        return path

    async def collect_knowledge(
        self,
        user_id: str,
        knowledge_point_id: str,
        folder: str = "默认收藏夹",
        note: str = ""
    ) -> bool:
        """
        收藏知识点

        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            folder: 收藏夹名称
            note: 备注

        Returns:
            bool: 是否收藏成功
        """
        if await self.learning_repo.is_collected(user_id, knowledge_point_id):
            return True

        collection = KnowledgeCollection.create(
            user_id=user_id,
            knowledge_point_id=knowledge_point_id,
            folder=folder,
            note=note
        )
        return await self.learning_repo.add_collection(collection)

    async def uncollect_knowledge(
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
        return await self.learning_repo.remove_collection(
            user_id, knowledge_point_id
        )

    async def get_user_collections(
        self,
        user_id: str,
        folder: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取用户收藏列表

        Args:
            user_id: 用户ID
            folder: 收藏夹过滤
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            List[Dict]: 收藏列表
        """
        collections = await self.learning_repo.get_collections_by_user(
            user_id, folder, limit, offset
        )

        result = []
        for col in collections:
            knowledge = await self.knowledge_repo.get_by_id(col.knowledge_point_id)
            if knowledge:
                result.append({
                    "collection_id": col.id,
                    "knowledge": knowledge.to_dict(),
                    "folder": col.folder,
                    "note": col.note,
                    "created_at": col.created_at.isoformat(),
                })
        return result

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
        return await self.learning_repo.is_collected(user_id, knowledge_point_id)

    async def get_user_folders(self, user_id: str) -> List[str]:
        """
        获取用户收藏夹列表

        Args:
            user_id: 用户ID

        Returns:
            List[str]: 收藏夹名称列表
        """
        return await self.learning_repo.get_user_folders(user_id)

    async def create_folder(
        self,
        user_id: str,
        folder_name: str
    ) -> bool:
        """
        创建收藏夹

        Args:
            user_id: 用户ID
            folder_name: 收藏夹名称

        Returns:
            bool: 是否创建成功
        """
        return await self.learning_repo.create_folder(user_id, folder_name)

    async def delete_folder(
        self,
        user_id: str,
        folder_name: str
    ) -> bool:
        """
        删除收藏夹

        Args:
            user_id: 用户ID
            folder_name: 收藏夹名称

        Returns:
            bool: 是否删除成功
        """
        return await self.learning_repo.delete_folder(user_id, folder_name)

    async def recommend_knowledge(
        self,
        user_id: str,
        current_knowledge_id: Optional[str] = None,
        limit: int = 5
    ) -> List[KnowledgePoint]:
        """
        推荐知识点

        Args:
            user_id: 用户ID
            current_knowledge_id: 当前知识点ID
            limit: 返回数量限制

        Returns:
            List[KnowledgePoint]: 推荐的知识点列表
        """
        recommendations = []

        if current_knowledge_id:
            prerequisites = await self.knowledge_repo.get_prerequisites(
                current_knowledge_id
            )
            recommendations.extend(prerequisites[:2])

            successors = await self.knowledge_repo.get_successors(
                current_knowledge_id
            )
            recommendations.extend(successors[:2])

        recent_path = await self.learning_repo.get_recent_learning_path(
            user_id, limit=5
        )
        if recent_path:
            last_knowledge = await self.knowledge_repo.get_by_id(recent_path[-1])
            if last_knowledge:
                search_results = await self.knowledge_repo.search(
                    last_knowledge.title,
                    course=last_knowledge.course,
                    limit=3
                )
                recommendations.extend([
                    r.knowledge_point for r in search_results
                    if r.knowledge_point.id not in recent_path
                ])

        user_stats = await self.learning_repo.get_user_stats(user_id)
        viewed_ids = [
            r.knowledge_point_id for r in user_stats.recent_activities
        ]

        unique_recommendations = []
        seen_ids = set()
        for kp in recommendations:
            if kp.id not in seen_ids and kp.id not in viewed_ids:
                unique_recommendations.append(kp)
                seen_ids.add(kp.id)
                if len(unique_recommendations) >= limit:
                    break

        return unique_recommendations

    async def get_learning_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取学习历史

        Args:
            user_id: 用户ID
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            List[Dict]: 学习历史列表
        """
        records = await self.learning_repo.get_records_by_user(
            user_id, limit, offset
        )

        history = []
        for record in records:
            knowledge = await self.knowledge_repo.get_by_id(
                record.knowledge_point_id
            )
            if knowledge:
                history.append({
                    "record": record.to_dict(),
                    "knowledge": {
                        "id": knowledge.id,
                        "title": knowledge.title,
                        "course": knowledge.course,
                        "chapter": knowledge.chapter,
                    }
                })
        return history
