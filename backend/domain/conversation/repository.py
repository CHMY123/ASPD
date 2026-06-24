"""
会话仓储接口 (ConversationRepository Interface)

定义会话数据访问的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.conversation.entity import Conversation, Message


class ConversationRepository(ABC):
    """
    会话仓储接口

    定义会话和消息数据访问的抽象接口。
    """

    @abstractmethod
    async def init_schema(self) -> None:
        """
        初始化数据库模式
        """
        pass

    @abstractmethod
    async def create_conversation(self, conversation: Conversation) -> bool:
        """
        创建新会话

        Args:
            conversation: 会话实体

        Returns:
            bool: 是否创建成功
        """
        pass

    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        获取会话

        Args:
            conversation_id: 会话ID

        Returns:
            Optional[Conversation]: 会话实体，不存在则返回None
        """
        pass

    @abstractmethod
    async def get_conversations_by_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """
        获取用户的所有会话

        Args:
            user_id: 用户ID
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            List[Conversation]: 会话列表
        """
        pass

    @abstractmethod
    async def update_conversation(self, conversation: Conversation) -> bool:
        """
        更新会话

        Args:
            conversation: 会话实体

        Returns:
            bool: 是否更新成功
        """
        pass

    @abstractmethod
    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        删除会话

        Args:
            conversation_id: 会话ID

        Returns:
            bool: 是否删除成功
        """
        pass

    @abstractmethod
    async def add_message(self, message: Message) -> bool:
        """
        添加消息

        Args:
            message: 消息实体

        Returns:
            bool: 是否添加成功
        """
        pass

    @abstractmethod
    async def get_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """
        获取会话的消息列表

        Args:
            conversation_id: 会话ID
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            List[Message]: 消息列表
        """
        pass

    @abstractmethod
    async def get_recent_messages(
        self,
        conversation_id: str,
        count: int = 10
    ) -> List[Message]:
        """
        获取最近的N条消息

        Args:
            conversation_id: 会话ID
            count: 消息数量

        Returns:
            List[Message]: 消息列表（按时间正序）
        """
        pass

    @abstractmethod
    async def count_messages(self, conversation_id: str) -> int:
        """
        获取会话的消息数量

        Args:
            conversation_id: 会话ID

        Returns:
            int: 消息数量
        """
        pass

    @abstractmethod
    async def delete_messages(self, conversation_id: str) -> bool:
        """
        删除会话的所有消息

        Args:
            conversation_id: 会话ID

        Returns:
            bool: 是否删除成功
        """
        pass
