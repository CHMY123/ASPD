"""
学习Schema定义

定义学习相关的请求和响应模型。
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class LearningRecordRequest(BaseModel):
    """学习记录请求"""
    user_id: str = Field(
        ...,
        description="用户标识"
    )
    knowledge_point_id: str = Field(
        ...,
        description="知识点标识"
    )
    action: str = Field(
        ...,
        description="操作类型：view/search/collect/ask",
        pattern="^(view|search|collect|ask|browse|review)$"
    )
    duration: int = Field(
        default=0,
        ge=0,
        description="停留时长（秒）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_001",
                "knowledge_point_id": "数据结构_二叉树",
                "action": "view",
                "duration": 120
            }
        }


class LearningRecordResponse(BaseModel):
    """学习记录响应"""
    success: bool = Field(description="是否成功")
    record_id: str = Field(description="记录ID")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "record_id": "rec_20240501001"
            }
        }


class LearningRecordItem(BaseModel):
    """学习记录项"""
    id: str = Field(description="记录ID")
    user_id: str = Field(description="用户ID")
    knowledge_point_id: str = Field(description="知识点ID")
    action: str = Field(description="操作类型")
    duration: int = Field(description="停留时长")
    created_at: datetime = Field(description="操作时间")


class LearningHistoryResponse(BaseModel):
    """学习历史响应"""
    records: List[LearningRecordItem] = Field(
        default_factory=list,
        description="学习记录列表"
    )
    total: int = Field(description="总数")


class LearningStatsResponse(BaseModel):
    """学习统计响应"""
    user_id: str = Field(description="用户ID")
    total_views: int = Field(description="总浏览次数")
    total_searches: int = Field(description="总搜索次数")
    total_questions: int = Field(description="总提问次数")
    total_collections: int = Field(description="总收藏数")
    total_duration: int = Field(description="总学习时长（秒）")
    knowledge_coverage: float = Field(description="知识点覆盖率")


class CollectionRequest(BaseModel):
    """收藏请求"""
    user_id: str = Field(
        ...,
        description="用户ID"
    )
    knowledge_point_id: str = Field(
        ...,
        description="知识点ID"
    )
    folder: str = Field(
        default="默认收藏夹",
        description="收藏夹名称"
    )
    note: str = Field(
        default="",
        description="用户备注"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_001",
                "knowledge_point_id": "数据结构_二叉树",
                "folder": "数据结构重点",
                "note": "需要重点复习"
            }
        }


class CollectionItem(BaseModel):
    """收藏项"""
    collection_id: str = Field(description="收藏ID")
    knowledge: dict = Field(description="知识点信息")
    folder: str = Field(description="收藏夹名称")
    note: str = Field(description="用户备注")
    created_at: datetime = Field(description="收藏时间")


class CollectionResponse(BaseModel):
    """收藏响应"""
    collections: List[CollectionItem] = Field(
        default_factory=list,
        description="收藏列表"
    )
    total: int = Field(description="总数")


class FolderRequest(BaseModel):
    """收藏夹请求"""
    user_id: str = Field(
        ...,
        description="用户ID"
    )
    folder_name: str = Field(
        ...,
        description="收藏夹名称"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_001",
                "folder_name": "数据结构重点"
            }
        }


class FolderListResponse(BaseModel):
    """收藏夹列表响应"""
    folders: List[str] = Field(
        default_factory=list,
        description="收藏夹名称列表"
    )


class LearningPathItem(BaseModel):
    """学习路径项"""
    id: str = Field(description="知识点ID")
    title: str = Field(description="知识点标题")
    course: str = Field(description="所属课程")


class LearningPathResponse(BaseModel):
    """学习路径响应"""
    path: List[LearningPathItem] = Field(
        default_factory=list,
        description="学习路径列表"
    )


class RecommendationRequest(BaseModel):
    """推荐请求"""
    user_id: str = Field(
        ...,
        description="用户ID"
    )
    current_knowledge_id: Optional[str] = Field(
        default=None,
        description="当前知识点ID"
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="返回数量限制"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_001",
                "current_knowledge_id": "数据结构_二叉树",
                "limit": 5
            }
        }


class RecommendationResponse(BaseModel):
    """推荐响应"""
    recommendations: List[dict] = Field(
        default_factory=list,
        description="推荐的知识点列表"
    )
    total: int = Field(description="总数")
