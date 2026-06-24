"""
会话实体 (Conversation and Message Entities)

定义问答会话的数据结构。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid


@dataclass
class Conversation:
    """
    会话实体

    Attributes:
        id: 会话唯一标识符（UUID）
        user_id: 用户ID
        title: 会话标题（自动生成或用户自定义）
        created_at: 创建时间
        updated_at: 最后活跃时间
        message_count: 消息数量
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    title: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    message_count: int = 0

    def update_activity(self):
        """更新最后活跃时间"""
        self.updated_at = datetime.now()
        self.message_count += 1

    def generate_title(self, first_message: str, max_length: int = 50) -> str:
        """
        根据首条消息生成会话标题

        Args:
            first_message: 首条消息内容
            max_length: 最大长度

        Returns:
            str: 生成的标题
        """
        if len(first_message) <= max_length:
            self.title = first_message
        else:
            self.title = first_message[:max_length-3] + "..."
        return self.title

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 字典表示
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "message_count": self.message_count,
        }


@dataclass
class Message:
    """
    消息实体

    Attributes:
        id: 消息唯一标识符
        conversation_id: 所属会话ID
        role: 角色（user/assistant/system）
        content: 消息内容
        references: 引用的知识点信息列表（完整信息，包含id、title、source、course、original_doc等）
        agent_used: 使用的Agent名称（用于多Agent协同对话）
        workflow_details: 工作流详情（包含参与Agent信息、执行步骤、推理过程等）
        created_at: 创建时间
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = ""
    role: str = ""
    content: str = ""
    references: List[dict] = field(default_factory=list)
    agent_used: str = ""
    workflow_details: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def is_user_message(self) -> bool:
        """是否为用户消息"""
        return self.role == "user"

    @property
    def is_assistant_message(self) -> bool:
        """是否为助手消息"""
        return self.role == "assistant"

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 字典表示
        """
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "references": self.references,
            "agent_used": self.agent_used,
            "workflow_details": self.workflow_details,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def user_message(
        cls,
        conversation_id: str,
        content: str
    ) -> "Message":
        """
        创建用户消息

        Args:
            conversation_id: 会话ID
            content: 消息内容

        Returns:
            Message: 用户消息实例
        """
        return cls(
            conversation_id=conversation_id,
            role="user",
            content=content,
        )

    @classmethod
    def assistant_message(
        cls,
        conversation_id: str,
        content: str,
        references: Optional[List[str]] = None,
        agent_used: str = "",
        workflow_details: Optional[dict] = None
    ) -> "Message":
        """
        创建助手消息

        Args:
            conversation_id: 会话ID
            content: 消息内容
            references: 引用的知识点ID列表
            agent_used: 使用的Agent名称
            workflow_details: 工作流详情（包含参与Agent信息、执行步骤、推理过程等）

        Returns:
            Message: 助手消息实例
        """
        return cls(
            conversation_id=conversation_id,
            role="assistant",
            content=content,
            references=references or [],
            agent_used=agent_used,
            workflow_details=workflow_details or {},
        )

    @classmethod
    def system_message(cls, content: str) -> "Message":
        """
        创建系统消息

        Args:
            content: 消息内容

        Returns:
            Message: 系统消息实例
        """
        return cls(
            conversation_id="",
            role="system",
            content=content,
        )
