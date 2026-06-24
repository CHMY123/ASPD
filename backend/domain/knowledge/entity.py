"""
知识点实体 (KnowledgePoint Entity)

定义知识点的核心数据结构。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import hashlib


@dataclass(frozen=True)
class KnowledgePoint:
    """
    知识点实体

    Attributes:
        id: 唯一标识符（由 source_file + title 生成哈希）
        title: 知识点标题
        content: 知识点正文内容
        course: 所属课程名称
        chapter: 所属章节
        tags: 标签列表
        source_file: 来源文件名
        prerequisites: 前置知识点ID列表
        successors: 后置知识点ID列表
        related_ids: 相关知识点ID列表
        embedding: 向量表示（1536维）
        created_at: 创建时间
        updated_at: 更新时间
        version: 版本号，用于版本管理
    """
    id: str
    title: str
    content: str
    course: str
    chapter: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    source_file: str = ""
    prerequisites: List[str] = field(default_factory=list)
    successors: List[str] = field(default_factory=list)
    related_ids: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: int = 1

    @classmethod
    def create_id(cls, source_file: str, title: str) -> str:
        """
        根据来源文件和问题生成唯一标识符

        Args:
            source_file: 来源文件名
            title: 知识点标题

        Returns:
            str: 生成的唯一标识符
        """
        raw = f"{source_file}:{title}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def with_embedding(self, embedding: List[float]) -> "KnowledgePoint":
        """
        创建带有向量表示的新实例

        Args:
            embedding: 向量表示

        Returns:
            KnowledgePoint: 包含向量表示的新实例
        """
        return KnowledgePoint(
            id=self.id,
            title=self.title,
            content=self.content,
            course=self.course,
            chapter=self.chapter,
            tags=self.tags,
            source_file=self.source_file,
            prerequisites=self.prerequisites,
            successors=self.successors,
            related_ids=self.related_ids,
            embedding=embedding,
            created_at=self.created_at,
            updated_at=self.updated_at,
            version=self.version,
        )

    def to_text(self) -> str:
        """
        将知识点转换为文本表示，用于生成向量

        Returns:
            str: 知识点文本表示
        """
        return f"{self.title}\n{self.content}"


@dataclass
class KnowledgeSearchResult:
    """
    知识检索结果

    Attributes:
        knowledge_point: 匹配的知识点
        score: 相似度分数
        rank: 排名
    """
    knowledge_point: KnowledgePoint
    score: float
    rank: int = 0

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            dict: 字典表示
        """
        return {
            "id": self.knowledge_point.id,
            "title": self.knowledge_point.title,
            "content": self.knowledge_point.content,
            "course": self.knowledge_point.course,
            "chapter": self.knowledge_point.chapter,
            "score": self.score,
        }


@dataclass
class ImportResult:
    """
    导入结果

    Attributes:
        total: 总数
        imported: 成功导入数
        failed: 失败数
        errors: 错误列表
    """
    total: int = 0
    imported: int = 0
    failed: int = 0
    errors: List[dict] = field(default_factory=list)

    def add_success(self):
        """增加成功计数"""
        self.imported += 1
        self.total += 1

    def add_failure(self, file: str, line: int, error: str):
        """
        增加失败计数

        Args:
            file: 文件名
            line: 行号
            error: 错误信息
        """
        self.failed += 1
        self.total += 1
        self.errors.append({
            "file": file,
            "line": line,
            "error": error
        })
