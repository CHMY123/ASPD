"""
学习记录仓储实现 (MySQL Learning Repository)

实现LearningRepository接口。
"""

import logging
from typing import List, Optional
from domain.learning.entity import LearningRecord, KnowledgeCollection, LearningStats
from domain.learning.repository import LearningRepository
from infrastructure.database import execute_sql, fetch_sql, fetchrow_sql

logger = logging.getLogger(__name__)


class PgLearningRepository(LearningRepository):
    """
    MySQL学习记录仓储实现
    """

    async def init_schema(self) -> None:
        """初始化数据库模式（已移至database_init.py统一处理）"""
        logger.info("学习记录表初始化已由DatabaseInitializer统一处理")

    async def add_record(self, record: LearningRecord) -> bool:
        """添加学习记录"""
        try:
            await execute_sql("""
                INSERT INTO learning_records
                (id, user_id, knowledge_point_id, action, duration, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                record.id,
                record.user_id,
                record.knowledge_point_id,
                record.action,
                record.duration,
                record.created_at
            )
            return True
        except Exception as e:
            logger.error(f"添加学习记录失败: {e}")
            return False

    async def get_records_by_user(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[LearningRecord]:
        """获取用户的学习记录"""
        rows = await fetch_sql("""
            SELECT * FROM learning_records
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, user_id, limit, offset)

        return [self._row_to_record(row) for row in rows]

    async def get_records_by_knowledge(
        self,
        knowledge_point_id: str,
        limit: int = 50
    ) -> List[LearningRecord]:
        """获取知识点的所有学习记录"""
        rows = await fetch_sql("""
            SELECT * FROM learning_records
            WHERE knowledge_point_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, knowledge_point_id, limit)

        return [self._row_to_record(row) for row in rows]

    async def get_user_stats(self, user_id: str) -> LearningStats:
        """获取用户学习统计"""
        total_row = await fetchrow_sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN action = 'view' THEN 1 ELSE 0 END) as views,
                SUM(CASE WHEN action = 'search' THEN 1 ELSE 0 END) as searches,
                SUM(CASE WHEN action = 'ask' THEN 1 ELSE 0 END) as questions,
                SUM(duration) as total_duration
            FROM learning_records
            WHERE user_id = %s
        """, user_id)

        collection_row = await fetchrow_sql("""
            SELECT COUNT(*) as count FROM knowledge_collections
            WHERE user_id = %s
        """, user_id)

        recent_records = await fetch_sql("""
            SELECT * FROM learning_records
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 10
        """, user_id)

        return LearningStats(
            user_id=user_id,
            total_views=total_row["views"] if total_row["views"] else 0,
            total_searches=total_row["searches"] if total_row["searches"] else 0,
            total_questions=total_row["questions"] if total_row["questions"] else 0,
            total_collections=collection_row["count"] if collection_row else 0,
            total_duration=total_row["total_duration"] if total_row["total_duration"] else 0,
            recent_activities=[self._row_to_record(r) for r in recent_records]
        )

    async def add_collection(self, collection: KnowledgeCollection) -> bool:
        """添加知识收藏"""
        try:
            await execute_sql("""
                INSERT INTO knowledge_collections
                (id, user_id, knowledge_point_id, folder, created_at, note)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE folder=VALUES(folder), note=VALUES(note)
            """,
                collection.id,
                collection.user_id,
                collection.knowledge_point_id,
                collection.folder,
                collection.created_at,
                collection.note
            )
            return True
        except Exception as e:
            logger.error(f"添加收藏失败: {e}")
            return False

    async def remove_collection(
        self,
        user_id: str,
        knowledge_point_id: str
    ) -> bool:
        """取消收藏"""
        try:
            await execute_sql("""
                DELETE FROM knowledge_collections
                WHERE user_id = %s AND knowledge_point_id = %s
            """, user_id, knowledge_point_id)
            return True
        except Exception as e:
            logger.error(f"取消收藏失败: {e}")
            return False

    async def get_collections_by_user(
        self,
        user_id: str,
        folder: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[KnowledgeCollection]:
        """获取用户的收藏列表"""
        if folder:
            rows = await fetch_sql("""
                SELECT * FROM knowledge_collections
                WHERE user_id = %s AND folder = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, user_id, folder, limit, offset)
        else:
            rows = await fetch_sql("""
                SELECT * FROM knowledge_collections
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, user_id, limit, offset)

        return [self._row_to_collection(row) for row in rows]

    async def is_collected(
        self,
        user_id: str,
        knowledge_point_id: str
    ) -> bool:
        """检查是否已收藏"""
        row = await fetchrow_sql("""
            SELECT 1 FROM knowledge_collections
            WHERE user_id = %s AND knowledge_point_id = %s
        """, user_id, knowledge_point_id)
        return row is not None

    async def get_user_folders(self, user_id: str) -> List[str]:
        """获取用户的收藏夹列表"""
        rows = await fetch_sql("""
            SELECT DISTINCT folder FROM knowledge_collections
            WHERE user_id = %s
            ORDER BY folder
        """, user_id)
        return [row["folder"] for row in rows]

    async def create_folder(self, user_id: str, folder_name: str) -> bool:
        """创建收藏夹"""
        try:
            collection = KnowledgeCollection(
                user_id=user_id,
                knowledge_point_id=f"__folder__{folder_name}",
                folder=folder_name
            )
            return await self.add_collection(collection)
        except Exception as e:
            logger.error(f"创建收藏夹失败: {e}")
            return False

    async def delete_folder(self, user_id: str, folder_name: str) -> bool:
        """删除收藏夹"""
        try:
            await execute_sql("""
                DELETE FROM knowledge_collections
                WHERE user_id = %s AND folder = %s
            """, user_id, folder_name)
            return True
        except Exception as e:
            logger.error(f"删除收藏夹失败: {e}")
            return False

    async def get_recent_learning_path(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[str]:
        """获取用户最近的学习路径"""
        rows = await fetch_sql("""
            SELECT knowledge_point_id 
            FROM learning_records
            WHERE user_id = %s AND action IN ('view', 'ask')
            GROUP BY knowledge_point_id
            ORDER BY MAX(created_at) DESC
            LIMIT %s
        """, user_id, limit)
        return [row["knowledge_point_id"] for row in rows]

    def _row_to_record(self, row: dict) -> LearningRecord:
        """将数据库行转换为学习记录实体"""
        return LearningRecord(
            id=row["id"],
            user_id=row["user_id"],
            knowledge_point_id=row["knowledge_point_id"],
            action=row["action"],
            duration=row["duration"] or 0,
            created_at=row["created_at"],
        )

    def _row_to_collection(self, row: dict) -> KnowledgeCollection:
        """将数据库行转换为收藏实体"""
        return KnowledgeCollection(
            id=row["id"],
            user_id=row["user_id"],
            knowledge_point_id=row["knowledge_point_id"],
            folder=row["folder"],
            created_at=row["created_at"],
            note=row["note"] or "",
        )
