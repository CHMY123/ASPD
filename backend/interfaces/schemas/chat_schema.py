"""
问答Schema定义

定义问答相关的请求和响应模型。
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """问答请求"""
    message: str = Field(
        ...,
        description="用户输入的问题文本",
        max_length=1000,
        examples=["什么是二叉树？", "请解释一下快速排序算法"]
    )
    thread_id: str = Field(
        ...,
        description="会话唯一标识，用于维护多轮对话上下文",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    user_id: Optional[str] = Field(
        default="anonymous",
        description="用户ID"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "什么是平衡二叉树？",
                "thread_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_001"
            }
        }


class ReferenceItem(BaseModel):
    """参考来源项"""
    id: str = Field(description="知识点ID")
    title: str = Field(description="知识点标题")
    source: Optional[str] = Field(default="", description="来源文件")
    original_doc: Optional[str] = Field(default="", description="原始文档名称")
    course: Optional[str] = Field(default="", description="所属课程")
    score: Optional[float] = Field(default=0, description="匹配分数")


class ChatResponse(BaseModel):
    """问答响应"""
    reply: str = Field(description="生成的回复文本")
    references: List[ReferenceItem] = Field(
        default_factory=list,
        description="参考的知识来源列表"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "reply": "平衡二叉树（AVL树）是一种特殊的二叉搜索树...",
                "references": [
                    {
                        "id": "数据结构_平衡二叉树",
                        "title": "平衡二叉树",
                        "source": "数据结构.md"
                    }
                ]
            }
        }


class ConversationResponse(BaseModel):
    """会话信息响应"""
    id: str = Field(description="会话ID")
    user_id: str = Field(description="用户ID")
    title: str = Field(description="会话标题")
    message_count: int = Field(description="消息数量")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="最后更新时间")

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """消息响应"""
    id: str = Field(description="消息ID")
    conversation_id: str = Field(description="会话ID")
    role: str = Field(description="角色（user/assistant/system）")
    content: str = Field(description="消息内容")
    references: List[ReferenceItem] = Field(default_factory=list, description="引用的知识点信息")
    created_at: datetime = Field(description="创建时间")

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(description="用户友好的错误提示")
    detail: Optional[str] = Field(default=None, description="技术详细错误信息")
    code: Optional[str] = Field(default=None, description="错误代码")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "抱歉，系统处理您的请求时出错，请稍后重试。",
                "detail": "知识库检索超时",
                "code": "RETRIEVAL_TIMEOUT"
            }
        }
