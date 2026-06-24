"""
知识库Schema定义

定义知识库相关的请求和响应模型。
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class KnowledgePointBase(BaseModel):
    """知识点基础模型"""
    id: str = Field(description="知识点ID")
    title: str = Field(description="知识点标题")
    content: str = Field(description="知识点正文内容")
    course: str = Field(description="所属课程名称")
    chapter: Optional[str] = Field(default=None, description="所属章节")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    source_file: str = Field(description="来源文件名")


class KnowledgePointResponse(KnowledgePointBase):
    """知识点响应"""
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    class Config:
        from_attributes = True


class KnowledgeSearchRequest(BaseModel):
    """知识检索请求"""
    query: str = Field(
        ...,
        description="检索关键词",
        min_length=1,
        max_length=200
    )
    course: Optional[str] = Field(
        default=None,
        description="按课程过滤"
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
                "query": "二叉树",
                "course": "数据结构",
                "limit": 5
            }
        }


class KnowledgeSearchResult(BaseModel):
    """知识检索结果项"""
    id: str = Field(description="知识点ID")
    title: str = Field(description="知识点标题")
    content: str = Field(description="知识点内容摘要")
    course: str = Field(description="所属课程")
    chapter: Optional[str] = Field(default=None, description="所属章节")
    score: float = Field(description="相似度分数")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "数据结构_二叉树",
                "title": "二叉树",
                "content": "二叉树是每个节点最多有两个子树的树结构...",
                "course": "数据结构",
                "chapter": "第五章 树与二叉树",
                "score": 0.95
            }
        }


class KnowledgeSearchResponse(BaseModel):
    """知识检索响应"""
    results: List[KnowledgeSearchResult] = Field(
        default_factory=list,
        description="检索结果列表"
    )
    total: int = Field(description="结果总数")


class KnowledgeImportRequest(BaseModel):
    """知识导入请求"""
    folder_path: str = Field(
        ...,
        description="知识库文件夹路径"
    )
    course_filter: Optional[List[str]] = Field(
        default=None,
        description="课程过滤条件，仅导入指定课程的文件"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "folder_path": "docs/knowledge/",
                "course_filter": ["数据结构", "算法基础"]
            }
        }


class ImportError(BaseModel):
    """导入错误项"""
    file: str = Field(description="文件名")
    line: int = Field(description="行号")
    error: str = Field(description="错误信息")


class KnowledgeImportResponse(BaseModel):
    """知识导入响应"""
    success: bool = Field(description="是否成功")
    total: int = Field(description="总数")
    imported: int = Field(description="成功导入数")
    failed: int = Field(description="失败数")
    errors: List[ImportError] = Field(
        default_factory=list,
        description="错误列表"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total": 15,
                "imported": 14,
                "failed": 1,
                "errors": [
                    {
                        "file": "docs/knowledge/算法基础.md",
                        "line": 45,
                        "error": "格式解析错误：缺少必要的标题字段"
                    }
                ]
            }
        }


class KnowledgeDetailResponse(BaseModel):
    """知识点详情响应"""
    id: str = Field(description="知识点ID")
    title: str = Field(description="知识点标题")
    content: str = Field(description="知识点正文")
    course: str = Field(description="所属课程")
    chapter: Optional[str] = Field(default=None, description="所属章节")
    tags: List[str] = Field(default_factory=list, description="标签")
    source_file: str = Field(description="来源文件")
    prerequisites: List[KnowledgePointBase] = Field(
        default_factory=list,
        description="前置知识点"
    )
    successors: List[KnowledgePointBase] = Field(
        default_factory=list,
        description="后置知识点"
    )
    related: List[KnowledgePointBase] = Field(
        default_factory=list,
        description="相关知识点"
    )


class KnowledgeUpdateRequest(BaseModel):
    """知识点更新请求"""
    title: Optional[str] = Field(default=None, description="知识点标题")
    content: Optional[str] = Field(default=None, description="知识点正文")
    chapter: Optional[str] = Field(default=None, description="所属章节")
    tags: Optional[List[str]] = Field(default=None, description="标签列表")
    prerequisites: Optional[List[str]] = Field(
        default=None,
        description="前置知识点ID列表"
    )
    successors: Optional[List[str]] = Field(
        default=None,
        description="后置知识点ID列表"
    )
    related_ids: Optional[List[str]] = Field(
        default=None,
        description="相关知识点ID列表"
    )


class CourseListResponse(BaseModel):
    """课程列表响应"""
    courses: List[str] = Field(description="课程名称列表")
    total: int = Field(description="课程总数")


class KnowledgeCountResponse(BaseModel):
    """知识点统计响应"""
    count: int = Field(description="知识点总数")
    courses: List[str] = Field(description="课程列表")
