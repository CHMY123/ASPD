"""
Agent工具工厂函数 (Agent Tools Factory)

定义Agent可调用的工具函数。
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any, TYPE_CHECKING
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from application.knowledge_service import KnowledgeService
    from application.learning_service import LearningService


class SearchKnowledgeInput(BaseModel):
    """搜索知识库输入参数"""
    query: str = Field(description="搜索查询文本，描述用户想了解的内容")
    course: Optional[str] = Field(default=None, description="课程名称过滤（可选）")
    limit: int = Field(default=3, description="返回结果数量")


class KnowledgeDetailInput(BaseModel):
    """知识点详情输入参数"""
    knowledge_id: str = Field(description="知识点ID")


class RelatedKnowledgeInput(BaseModel):
    """相关知识点输入参数"""
    knowledge_id: str = Field(description="当前知识点ID")
    rel_type: str = Field(default="related", description="相关类型（prerequisites/successors/related）")


class RecordLearningInput(BaseModel):
    """记录学习行为输入参数"""
    user_id: str = Field(description="用户ID")
    knowledge_point_id: str = Field(description="知识点ID")
    action: str = Field(description="操作类型（view/ask/search）")
    duration: int = Field(default=0, description="停留时长（秒）")


class ToolAdapter:
    """
    工具适配器

    将服务方法适配为LangChain工具。
    """

    def __init__(
        self,
        knowledge_service: "KnowledgeService",
        learning_service: Optional["LearningService"] = None
    ):
        """
        初始化工具适配器

        Args:
            knowledge_service: 知识库应用服务
            learning_service: 学习应用服务
        """
        self.knowledge_service = knowledge_service
        self.learning_service = learning_service

    def get_tools(self) -> List[StructuredTool]:
        """
        获取所有可用工具

        Returns:
            List[StructuredTool]: 工具列表
        """
        tools = [
            self._create_search_tool(),
            self._create_detail_tool(),
            self._create_prerequisites_tool(),
            self._create_successors_tool(),
            self._create_related_tool(),
        ]

        if self.learning_service:
            tools.append(self._create_record_tool())

        return tools

    def _create_search_tool(self) -> StructuredTool:
        """创建搜索知识库工具"""
        async def _search(query: str, course: Optional[str] = None, limit: int = 3) -> str:
            return await self.search_knowledge(query, course, limit)

        return StructuredTool(
            name="search_knowledge",
            description="搜索知识库。当用户询问课程相关的问题时，首先使用此工具搜索相关知识点。",
            func=lambda query, course=None, limit=3: None,  # 同步占位
            coroutine=_search,
            args_schema=SearchKnowledgeInput
        )

    def _create_detail_tool(self) -> StructuredTool:
        """创建知识点详情工具"""
        async def _detail(knowledge_id: str) -> str:
            return await self.get_knowledge_detail(knowledge_id)

        return StructuredTool(
            name="get_knowledge_detail",
            description="获取知识点详情。获取指定知识点的详细内容，包括正文、关联知识点等信息。",
            func=lambda knowledge_id: None,
            coroutine=_detail,
            args_schema=KnowledgeDetailInput
        )

    def _create_prerequisites_tool(self) -> StructuredTool:
        """创建前置知识点工具"""
        async def _prereq(knowledge_id: str) -> str:
            return await self.get_related_knowledge(knowledge_id, "prerequisites")

        return StructuredTool(
            name="get_prerequisites",
            description="获取前置知识点。获取学习指定知识点前需要掌握的内容。",
            func=lambda knowledge_id: None,
            coroutine=_prereq,
            args_schema=KnowledgeDetailInput
        )

    def _create_successors_tool(self) -> StructuredTool:
        """创建后置知识点工具"""
        async def _succ(knowledge_id: str) -> str:
            return await self.get_related_knowledge(knowledge_id, "successors")

        return StructuredTool(
            name="get_successors",
            description="获取后置知识点。获取指定知识点之后可以继续学习的内容。",
            func=lambda knowledge_id: None,
            coroutine=_succ,
            args_schema=KnowledgeDetailInput
        )

    def _create_related_tool(self) -> StructuredTool:
        """创建相关知识点工具"""
        async def _related(knowledge_id: str, rel_type: str = "related") -> str:
            return await self.get_related_knowledge(knowledge_id, rel_type)

        return StructuredTool(
            name="get_related_knowledge",
            description="获取相关知识点。获取与当前知识点相关的内容。",
            func=lambda knowledge_id, rel_type="related": None,
            coroutine=_related,
            args_schema=RelatedKnowledgeInput
        )

    def _create_record_tool(self) -> StructuredTool:
        """创建学习记录工具"""
        async def _record(user_id: str, knowledge_point_id: str, action: str, duration: int = 0) -> str:
            return await self.record_learning(user_id, knowledge_point_id, action, duration)

        return StructuredTool(
            name="record_learning",
            description="记录学习行为。记录用户的学习行为，用于学习路径追踪和个性化推荐。",
            func=lambda user_id, knowledge_point_id, action, duration=0: None,
            coroutine=_record,
            args_schema=RecordLearningInput
        )

    async def search_knowledge(
        self,
        query: str,
        course: Optional[str] = None,
        limit: int = 3
    ) -> str:
        """
        搜索知识库

        Args:
            query: 搜索查询
            course: 课程过滤
            limit: 返回数量

        Returns:
            str: 格式化后的搜索结果
        """
        results = await self.knowledge_service.search_knowledge(
            query, course, limit
        )

        if not results:
            return "未找到相关知识点，请尝试其他问题或联系教师。"

        output = "找到以下相关知识点：\n\n"
        for i, result in enumerate(results, 1):
            kp = result.knowledge_point
            output += f"{i}. **{kp.title}** [{kp.course}]\n"
            output += f"   {kp.content[:200]}...\n"
            output += f"   参考来源：{kp.source_file}\n\n"

        return output

    async def get_knowledge_detail(self, knowledge_id: str) -> str:
        """
        获取知识点详情

        Args:
            knowledge_id: 知识点ID

        Returns:
            str: 知识点详情
        """
        result = await self.knowledge_service.get_knowledge_with_relations(
            knowledge_id
        )

        if not result:
            return "未找到该知识点"

        kp = result["knowledge"]
        output = f"## {kp.title}\n\n"
        output += f"**课程**: {kp.course}\n"
        if kp.chapter:
            output += f"**章节**: {kp.chapter}\n"
        output += f"\n{kp.content}\n\n"

        if result["prerequisites"]:
            output += "### 前置知识点\n"
            for prereq in result["prerequisites"]:
                output += f"- {prereq.title}\n"
            output += "\n"

        if result["successors"]:
            output += "### 后续学习\n"
            for succ in result["successors"]:
                output += f"- {succ.title}\n"
            output += "\n"

        return output

    async def get_related_knowledge(
        self,
        knowledge_id: str,
        rel_type: str = "related"
    ) -> str:
        """
        获取相关知识点

        Args:
            knowledge_id: 知识点ID
            rel_type: 相关类型

        Returns:
            str: 相关知识点列表
        """
        if rel_type == "prerequisites":
            items = await self.knowledge_service.suggest_prerequisites(
                knowledge_id
            )
            title = "前置知识点（建议先学习）"
        elif rel_type == "successors":
            items = await self.knowledge_service.suggest_successors(
                knowledge_id
            )
            title = "后续学习（拓展延伸）"
        else:
            result = await self.knowledge_service.get_knowledge_with_relations(
                knowledge_id
            )
            items = result.get("related", [])
            title = "相关知识点"

        if not items:
            return "暂无相关知识点"

        output = f"### {title}\n\n"
        for item in items:
            output += f"- **{item.title}** [{item.course}]\n"

        return output

    async def record_learning(
        self,
        user_id: str,
        knowledge_point_id: str,
        action: str,
        duration: int = 0
    ) -> str:
        """
        记录学习行为

        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            action: 操作类型
            duration: 停留时长

        Returns:
            str: 记录结果
        """
        if not self.learning_service:
            return "学习记录服务未启用"

        await self.learning_service.record_action(
            user_id, knowledge_point_id, action, duration
        )
        return "学习行为已记录"


def create_tools(
    knowledge_service: "KnowledgeService",
    learning_service: Optional["LearningService"] = None
) -> List[StructuredTool]:
    """
    创建Agent工具列表

    Args:
        knowledge_service: 知识库应用服务
        learning_service: 学习应用服务（可选）

    Returns:
        list: 工具函数列表
    """
    adapter = ToolAdapter(knowledge_service, learning_service)
    return adapter.get_tools()