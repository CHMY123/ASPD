"""
会话仓储实现 (MySQL Conversation Repository)

实现ConversationRepository接口。
"""

import json
import logging
from typing import List, Optional
from datetime import datetime
from domain.conversation.entity import Conversation, Message
from domain.conversation.repository import ConversationRepository
from infrastructure.database import execute_sql, fetch_sql, fetchrow_sql

logger = logging.getLogger(__name__)


class PgConversationRepository(ConversationRepository):
    """
    MySQL会话仓储实现
    """

    async def init_schema(self) -> None:
        """初始化数据库模式（已移至database_init.py统一处理）"""
        logger.info("会话表初始化已由DatabaseInitializer统一处理")

    async def create_conversation(self, conversation: Conversation) -> bool:
        """创建新会话"""
        try:
            await execute_sql("""
                INSERT INTO conversations (id, user_id, title, created_at, updated_at, message_count)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                conversation.id,
                conversation.user_id,
                conversation.title,
                conversation.created_at,
                conversation.updated_at,
                conversation.message_count
            )
            return True
        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            return False

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """获取会话"""
        row = await fetchrow_sql(
            "SELECT * FROM conversations WHERE id = %s",
            conversation_id
        )

        if not row:
            return None

        return self._row_to_conversation(row)

    async def get_conversations_by_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """获取用户的所有会话"""
        rows = await fetch_sql("""
            SELECT * FROM conversations
            WHERE user_id = %s
            ORDER BY updated_at DESC
            LIMIT %s OFFSET %s
        """, user_id, limit, offset)

        return [self._row_to_conversation(row) for row in rows]

    async def update_conversation(self, conversation: Conversation) -> bool:
        """更新会话"""
        try:
            await execute_sql("""
                UPDATE conversations
                SET title = %s, updated_at = %s, message_count = %s
                WHERE id = %s
            """,
                conversation.title,
                conversation.updated_at,
                conversation.message_count,
                conversation.id
            )
            return True
        except Exception as e:
            logger.error(f"更新会话失败: {e}")
            return False

    async def delete_conversation(self, conversation_id: str) -> bool:
        """删除会话"""
        try:
            await execute_sql(
                "DELETE FROM conversations WHERE id = %s",
                conversation_id
            )
            return True
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False

    async def add_message(self, message: Message) -> bool:
        """添加消息"""
        try:
            # 将references列表转换为JSON字符串
            refs_json = json.dumps(message.references) if message.references else None
            # 将workflow_details转换为JSON字符串
            workflow_json = json.dumps(message.workflow_details) if message.workflow_details else None
            
            await execute_sql("""
                INSERT INTO messages (id, conversation_id, role, content, `references`, agent_used, workflow_details, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
                message.id,
                message.conversation_id,
                message.role,
                message.content,
                refs_json,
                message.agent_used,
                workflow_json,
                message.created_at
            )

            await execute_sql("""
                UPDATE conversations
                SET message_count = message_count + 1, updated_at = %s
                WHERE id = %s
            """, datetime.now(), message.conversation_id)

            return True
        except Exception as e:
            logger.error(f"添加消息失败: {e}")
            return False

    async def get_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """获取会话的消息列表"""
        rows = await fetch_sql("""
            SELECT * FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC
            LIMIT %s OFFSET %s
        """, conversation_id, limit, offset)

        return [self._row_to_message(row) for row in rows]

    async def get_recent_messages(
        self,
        conversation_id: str,
        count: int = 10
    ) -> List[Message]:
        """获取最近的N条消息"""
        rows = await fetch_sql("""
            SELECT * FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, conversation_id, count)

        messages = [self._row_to_message(row) for row in rows]
        return list(reversed(messages))

    async def count_messages(self, conversation_id: str) -> int:
        """获取会话的消息数量"""
        row = await fetchrow_sql("""
            SELECT COUNT(*) as count FROM messages
            WHERE conversation_id = %s
        """, conversation_id)
        return row["count"] if row else 0

    async def delete_messages(self, conversation_id: str) -> bool:
        """删除会话的所有消息"""
        try:
            await execute_sql(
                "DELETE FROM messages WHERE conversation_id = %s",
                conversation_id
            )
            return True
        except Exception as e:
            logger.error(f"删除消息失败: {e}")
            return False

    def _row_to_conversation(self, row: dict) -> Conversation:
        """将数据库行转换为会话实体"""
        return Conversation(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"] or "",
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            message_count=row["message_count"] or 0,
        )

    def _row_to_message(self, row: dict) -> Message:
        """将数据库行转换为消息实体"""
        refs = row.get("references")
        
        # 处理NULL值
        if refs is None:
            refs = []
        elif isinstance(refs, str):
            try:
                refs = json.loads(refs)
            except (json.JSONDecodeError, TypeError):
                refs = []
        
        # 确保refs是列表
        if not isinstance(refs, list):
            refs = []
        
        # 处理兼容性：将旧格式（字符串列表）转换为新格式（字典列表）
        formatted_refs = []
        for ref in refs:
            if isinstance(ref, str):
                # 旧格式：字符串ID
                formatted_refs.append({"id": ref, "title": "", "source": "", "original_doc": "", "course": "", "score": 0})
            elif isinstance(ref, dict):
                # 新格式：字典，确保包含所有必要字段
                formatted_refs.append({
                    "id": ref.get("id", ""),
                    "title": ref.get("title", ""),
                    "source": ref.get("source", ""),
                    "original_doc": ref.get("original_doc", ""),
                    "course": ref.get("course", ""),
                    "score": ref.get("score", 0)
                })
            else:
                formatted_refs.append({"id": str(ref), "title": "", "source": "", "original_doc": "", "course": "", "score": 0})
        
        # 处理workflow_details
        workflow_details = row.get("workflow_details")
        if workflow_details is None:
            workflow_details = {}
        elif isinstance(workflow_details, str):
            try:
                workflow_details = json.loads(workflow_details)
            except (json.JSONDecodeError, TypeError):
                workflow_details = {}
        if not isinstance(workflow_details, dict):
            workflow_details = {}
        
        return Message(
            id=row["id"],
            conversation_id=row["conversation_id"],
            role=row["role"],
            content=row["content"],
            references=formatted_refs,
            agent_used=row.get("agent_used", ""),
            workflow_details=workflow_details,
            created_at=row["created_at"],
        )
