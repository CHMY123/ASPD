"""
知识库应用服务 (Knowledge Application Service)

处理知识点的导入、编辑、检索等业务逻辑。
实现基于RAG的智能问答检索流程。
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from domain.knowledge.entity import KnowledgePoint, KnowledgeSearchResult, ImportResult
from domain.knowledge.repository import KnowledgeRepository
from infrastructure.llm_client import LLMClient

# 初始化logger
logger = logging.getLogger(__name__)


class KnowledgeService:
    """
    知识库应用服务

    协调知识库领域对象和LLM服务，完成知识管理相关业务操作。

    Attributes:
        knowledge_repo: 知识库仓储接口
        llm_client: LLM客户端
    """

    def __init__(
        self,
        knowledge_repo: KnowledgeRepository,
        llm_client: LLMClient
    ):
        """
        初始化知识库服务

        Args:
            knowledge_repo: 知识库仓储接口
            llm_client: LLM客户端
        """
        self.knowledge_repo = knowledge_repo
        self.llm_client = llm_client

    async def initialize(self) -> None:
        """
        初始化知识库服务

        初始化数据库模式。
        """
        await self.knowledge_repo.init_schema()

    async def search(
        self,
        query: str,
        course: Optional[str] = None,
        limit: int = 5,
        use_rerank: bool = True
    ) -> List[KnowledgeSearchResult]:
        """
        语义检索知识点

        完整RAG检索流程：
        1. 向量检索（query:前缀）
        2. 关键词检索
        3. RRF融合
        4. Rerank精排（可选）

        Args:
            query: 查询文本
            course: 课程过滤
            limit: 返回数量
            use_rerank: 是否启用Rerank

        Returns:
            List[KnowledgeSearchResult]: 检索结果列表
        """
        return await self.knowledge_repo.search(
            query=query,
            course=course,
            limit=limit,
            use_rerank=use_rerank
        )

    async def import_from_folder(
        self,
        folder_path: str,
        course_filter: Optional[List[str]] = None
    ) -> ImportResult:
        """
        从文件夹批量导入知识库

        Args:
            folder_path: 文件夹路径
            course_filter: 课程过滤条件

        Returns:
            ImportResult: 导入结果
        """
        folder = Path(folder_path).resolve()
        if not folder.exists() or not folder.is_dir():
            result = ImportResult()
            result.add_failure(folder_path, 0, "文件夹不存在或不是有效目录")
            return result

        md_files = list(folder.glob("**/*.md"))
        result = ImportResult()
        knowledge_points = []

        for md_file in md_files:
            try:
                points = await self._parse_markdown_file(md_file)
                for point in points:
                    if course_filter and point.course not in course_filter:
                        continue
                    knowledge_points.append(point)
            except Exception as e:
                result.add_failure(str(md_file), 0, f"解析失败: {str(e)}")

        if knowledge_points:
            embed_result = await self._embed_knowledge_points(knowledge_points)
            result.imported = embed_result.imported
            result.failed = embed_result.failed
            result.errors.extend(embed_result.errors)
            result.total = len(knowledge_points)

        return result

    async def _parse_markdown_file(self, file_path: Path) -> List[KnowledgePoint]:
        """
        解析Markdown文件

        Args:
            file_path: 文件路径

        Returns:
            List[KnowledgePoint]: 知识点列表
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        course_name = file_path.stem
        knowledge_points = []

        sections = self._split_markdown_sections(content)

        for section in sections:
            if not section.get("title") or not section.get("content"):
                continue

            knowledge_point = KnowledgePoint(
                id=KnowledgePoint.create_id(str(file_path), section["title"]),
                title=section["title"],
                content=section["content"],
                course=course_name,
                chapter=section.get("parent_title", ""),
                tags=section.get("tags", []),
                source_file=str(file_path),
            )
            knowledge_points.append(knowledge_point)

        return knowledge_points

    def _split_markdown_sections(self, content: str) -> List[Dict[str, Any]]:
        """
        分割Markdown内容为多个章节

        支持 # ~ #### 所有标题级别，每个标题（不含 # H1）作为一个独立知识点。
        H1 不作为知识点，仅作为父标题（parent_title）。

        Args:
            content: Markdown内容

        Returns:
            List[Dict]: 章节列表
        """
        import re
        
        sections = []
        h1_title = ""
        h2_parent = ""

        # 统一按标题行分割
        # 匹配 # ~ ###### 标题，按出现的顺序处理
        lines = content.split("\n")
        current_section = None

        for line in lines:
            # 匹配标题行
            h1_match = re.match(r'^#\s+(.+)$', line)
            h2_match = re.match(r'^##\s+(.+)$', line)
            h3_match = re.match(r'^###\s+(.+)$', line)
            h4_match = re.match(r'^####\s+(.+)$', line)

            if h1_match:
                # H1：保存前一个section，记录为parent
                if current_section and current_section["title"]:
                    sections.append(current_section)
                h1_title = h1_match.group(1).strip()
                h2_parent = ""
                current_section = {"title": "", "content": "", "parent_title": h1_title, "tags": []}

            elif h2_match:
                # H2：保存前一个section，创建新section
                if current_section and current_section["title"]:
                    sections.append(current_section)
                h2_parent = h2_match.group(1).strip()
                current_section = {
                    "title": h2_parent,
                    "content": "",
                    "parent_title": h1_title,
                    "tags": self._extract_tags_from_content(content)
                }

            elif h3_match:
                # H3：保存前一个section，创建新section
                if current_section and current_section["title"]:
                    sections.append(current_section)
                current_section = {
                    "title": h3_match.group(1).strip(),
                    "content": "",
                    "parent_title": h2_parent or h1_title,
                    "tags": []
                }

            elif h4_match:
                # H4（如 1.1.1 数组）：作为独立知识点
                if current_section and current_section["title"]:
                    sections.append(current_section)
                current_section = {
                    "title": h4_match.group(1).strip(),
                    "content": "",
                    "parent_title": h2_parent or h1_title,
                    "tags": []
                }

            else:
                # 正文行：追加到当前 section
                if current_section is not None:
                    current_section["content"] += line + "\n"

        # 末尾 section
        if current_section and current_section["title"]:
            sections.append(current_section)

        for section in sections:
            section["content"] = section["content"].strip()
            # 去掉空内容 section
            if not section["content"]:
                section["content"] = section["title"]

        return sections

    def _extract_tags_from_content(self, content: str) -> List[str]:
        """
        从内容中提取标签

        Args:
            content: 内容

        Returns:
            List[str]: 标签列表
        """
        tag_pattern = r'`([^`]+)`'
        tags = re.findall(tag_pattern, content)
        return list(set(tags))[:5]

    async def _embed_knowledge_points(
        self,
        knowledge_points: List[KnowledgePoint]
    ) -> ImportResult:
        """
        为知识点生成向量并存储

        Args:
            knowledge_points: 知识点列表

        Returns:
            ImportResult: 导入结果
        """
        result = ImportResult()

        for point in knowledge_points:
            try:
                text = point.to_text()
                embedding = await self.llm_client.get_embedding(text)
                
                if not embedding or len(embedding) == 0:
                    result.add_failure(point.source_file, 0, "向量化返回空向量")
                    continue
                    
                point_with_embedding = point.with_embedding(embedding)
                success = await self.knowledge_repo.save(point_with_embedding)
                if success:
                    result.add_success()
                else:
                    result.add_failure(point.source_file, 0, "保存到向量数据库失败")
            except Exception as e:
                error_msg = f"向量化失败: {str(e)}"
                if "401" in str(e) or "Unauthorized" in str(e):
                    error_msg = "向量化失败: API密钥无效或未配置，请检查LLM_API_KEY环境变量"
                elif "403" in str(e) or "Forbidden" in str(e):
                    error_msg = "向量化失败: API访问被拒绝，请检查API密钥权限"
                elif "timeout" in str(e).lower():
                    error_msg = "向量化失败: 请求超时，请检查网络连接或稍后重试"
                elif "ConnectionRefusedError" in str(e) or "ConnectError" in str(e):
                    error_msg = "向量化失败: 无法连接到Embedding服务，请检查网络和API地址配置"
                logger.error(f"Embedding error for {point.title}: {error_msg}")
                result.add_failure(point.source_file, 0, error_msg)

        return result

    async def search_knowledge(
        self,
        query: str,
        course: Optional[str] = None,
        limit: int = 5
    ) -> List[KnowledgeSearchResult]:
        """
        检索知识点

        Args:
            query: 查询文本
            course: 课程过滤
            limit: 返回数量

        Returns:
            List[KnowledgeSearchResult]: 检索结果
        """
        return await self.knowledge_repo.search(query, course, limit)

    async def get_knowledge_by_id(
        self,
        knowledge_id: str
    ) -> Optional[KnowledgePoint]:
        """
        根据ID获取知识点

        Args:
            knowledge_id: 知识点ID

        Returns:
            Optional[KnowledgePoint]: 知识点
        """
        return await self.knowledge_repo.get_by_id(knowledge_id)

    async def get_knowledge_by_ids(
        self,
        knowledge_ids: List[str]
    ) -> List[KnowledgePoint]:
        """
        根据ID列表获取知识点

        Args:
            knowledge_ids: 知识点ID列表

        Returns:
            List[KnowledgePoint]: 知识点列表
        """
        return await self.knowledge_repo.get_by_ids(knowledge_ids)

    async def get_knowledge_with_relations(
        self,
        knowledge_id: str
    ) -> Dict[str, Any]:
        """
        获取知识点及其关联内容

        Args:
            knowledge_id: 知识点ID

        Returns:
            Dict: 包含知识点和关联内容的字典
        """
        knowledge = await self.knowledge_repo.get_by_id(knowledge_id)
        if not knowledge:
            return {}

        prerequisites = await self.knowledge_repo.get_prerequisites(knowledge_id)
        successors = await self.knowledge_repo.get_successors(knowledge_id)
        related = await self.knowledge_repo.get_related(knowledge_id)

        return {
            "knowledge": knowledge,
            "prerequisites": prerequisites,
            "successors": successors,
            "related": related,
        }

    async def update_knowledge(
        self,
        knowledge_point: KnowledgePoint
    ) -> bool:
        """
        更新知识点

        Args:
            knowledge_point: 知识点

        Returns:
            bool: 是否更新成功
        """
        return await self.knowledge_repo.update(knowledge_point)

    async def delete_knowledge(self, knowledge_id: str) -> bool:
        """
        删除知识点

        Args:
            knowledge_id: 知识点ID

        Returns:
            bool: 是否删除成功
        """
        return await self.knowledge_repo.delete(knowledge_id)

    async def get_all_courses(self) -> List[str]:
        """
        获取所有课程名称

        Returns:
            List[str]: 课程名称列表
        """
        return await self.knowledge_repo.get_courses()

    async def get_knowledge_by_course(
        self,
        course: str
    ) -> List[KnowledgePoint]:
        """
        获取课程的所有知识点

        Args:
            course: 课程名称

        Returns:
            List[KnowledgePoint]: 知识点列表
        """
        return await self.knowledge_repo.get_by_course(course)

    async def get_knowledge_count(self) -> int:
        """
        获取知识点总数

        Returns:
            int: 知识点数量
        """
        return await self.knowledge_repo.count()

    async def suggest_prerequisites(
        self,
        knowledge_id: str
    ) -> List[KnowledgePoint]:
        """
        建议前置知识点（推荐学习路径）

        Args:
            knowledge_id: 知识点ID

        Returns:
            List[KnowledgePoint]: 建议的前置知识点
        """
        knowledge = await self.knowledge_repo.get_by_id(knowledge_id)
        if not knowledge:
            return []

        prerequisites = await self.knowledge_repo.get_prerequisites(knowledge_id)
        if prerequisites:
            return prerequisites

        search_results = await self.knowledge_repo.search(
            knowledge.title,
            course=knowledge.course,
            limit=3
        )

        return [r.knowledge_point for r in search_results
                if r.knowledge_point.id != knowledge_id][:3]

    async def suggest_successors(
        self,
        knowledge_id: str
    ) -> List[KnowledgePoint]:
        """
        建议后置知识点（拓展学习）

        Args:
            knowledge_id: 知识点ID

        Returns:
            List[KnowledgePoint]: 建议的后置知识点
        """
        knowledge = await self.knowledge_repo.get_by_id(knowledge_id)
        if not knowledge:
            return []

        successors = await self.knowledge_repo.get_successors(knowledge_id)
        if successors:
            return successors

        course_knowledge = await self.knowledge_repo.get_by_course(knowledge.course)
        other_knowledge = [k for k in course_knowledge if k.id != knowledge_id]

        search_results = await self.knowledge_repo.search(
            knowledge.title,
            course=knowledge.course,
            limit=5
        )

        return [r.knowledge_point for r in search_results
                if r.knowledge_point.id != knowledge_id][:3]

    # ==================== RAG辅助方法 ====================

    def build_context(
        self,
        results: List[KnowledgeSearchResult],
        max_content_length: int = 800
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        构建RAG上下文

        将检索结果转换为适合LLM的上下文格式，包含文档来源信息。

        Args:
            results: 检索结果列表
            max_content_length: 最大内容长度

        Returns:
            Tuple[str, List[Dict]]: (上下文文本, 参考来源列表)
        """
        # 如果仓储实现了build_context方法，则委托给仓储
        if hasattr(self.knowledge_repo, 'build_context'):
            return self.knowledge_repo.build_context(results, max_content_length)

        # 否则使用默认实现
        context_parts = []
        references = []

        for idx, result in enumerate(results, 1):
            kp = result.knowledge_point

            # 截断内容
            content = kp.content[:max_content_length]
            if len(kp.content) > max_content_length:
                content += "..."

            # 构建上下文片段
            context_parts.append(
                f"【参考文档{idx}】\n"
                f"标题: {kp.title}\n"
                f"课程: {kp.course}\n"
                f"内容: {content}\n"
            )

            # 构建参考来源
            references.append({
                "id": kp.id,
                "title": kp.title,
                "source": kp.source_file,
                "course": kp.course,
                "score": round(result.score, 3)
            })

        context = "\n\n".join(context_parts)
        return context, references

    async def load_knowledge_base(self) -> ImportResult:
        """
        加载整个知识库目录

        从配置的KNOWLEDGE_BASE_PATH目录加载所有md文件

        Returns:
            ImportResult: 导入结果
        """
        # 如果仓储实现了load_knowledge_base方法，则委托给仓储
        if hasattr(self.knowledge_repo, 'load_knowledge_base'):
            return await self.knowledge_repo.load_knowledge_base()

        # 否则使用默认实现
        from config import KNOWLEDGE_BASE_PATH
        return await self.import_from_folder(KNOWLEDGE_BASE_PATH)
