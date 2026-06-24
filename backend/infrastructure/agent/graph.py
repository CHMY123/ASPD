"""
LangGraph Agent图构建 (LangGraph Agent Graph)

构建问答Agent，将LLM与工具绑定。
"""

from __future__ import annotations

from typing import Dict, Any, List, Literal, TypedDict, Annotated, TYPE_CHECKING
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages

from infrastructure.agent.tools import ToolAdapter
from infrastructure.llm_client import LLMClient

if TYPE_CHECKING:
    from application.knowledge_service import KnowledgeService
    from application.learning_service import LearningService


class AgentState(TypedDict):
    """Agent状态定义"""
    messages: Annotated[list, add_messages]
    references: List[str]
    reply: str


SYSTEM_PROMPT = """你是一个课程学习知识库问答系统的智能助手。

【核心指令-必须遵守】
1. 你只能使用下方【检索到的参考文档】中的信息来回答用户问题
2. 如果参考文档中没有相关信息，你必须直接回答："知识库中未找到与您问题相关的信息，请尝试其他问题或联系教师。"
3. 严禁使用你自身的训练数据中的知识来回答
4. 严禁编造或引用不存在的知识库信息
5. 回答完成后，列出你实际引用的参考来源标题

请用中文回答。"""

FALLBACK_SYSTEM_PROMPT = """你是一个课程学习知识库问答系统的智能助手。

【核心指令-必须遵守】
当前知识库中暂无与您问题相关的参考文档。

你必须直接回答："知识库中未找到与您问题相关的信息，请尝试其他问题或联系教师。"

严禁使用你自身的训练数据中的知识来回答。严禁编造任何信息。"""


class AgentGraph:
    """
    LangGraph问答Agent

    Attributes:
        knowledge_service: 知识库服务
        learning_service: 学习服务
        llm_client: LLM客户端
        tool_adapter: 工具适配器
        graph: LangGraph图
        checkpointer: 检查点存储器
    """

    def __init__(
        self,
        knowledge_service: KnowledgeService,
        learning_service: LearningService,
        llm_client: LLMClient
    ):
        """
        初始化Agent

        Args:
            knowledge_service: 知识库服务
            learning_service: 学习服务
            llm_client: LLM客户端
        """
        self.knowledge_service = knowledge_service
        self.learning_service = learning_service
        self.llm_client = llm_client
        self.tool_adapter = ToolAdapter(knowledge_service, learning_service)
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        构建LangGraph图

        Returns:
            StateGraph: 构建好的图
        """
        graph = StateGraph(AgentState)

        graph.add_node("llm_node", self._llm_node)
        graph.add_node("tools_node", self._tools_node)

        graph.add_edge("__start__", "llm_node")

        graph.add_conditional_edges(
            "llm_node",
            self._should_use_tools,
            {
                "use_tools": "tools_node",
                "END": END
            }
        )

        graph.add_edge("tools_node", "llm_node")

        return graph.compile(checkpointer=self.checkpointer)

    def _should_use_tools(self, state: AgentState) -> Literal["use_tools", "END"]:
        """
        判断是否需要使用工具

        Args:
            state: 当前状态

        Returns:
            str: 下一个节点
        """
        messages = state.get("messages", [])
        if not messages:
            return "END"

        last_message = messages[-1]
        if isinstance(last_message, AIMessage):
            if last_message.tool_calls:
                return "use_tools"
            return "END"

        return "END"

    async def _llm_node(self, state: AgentState) -> Dict[str, Any]:
        """
        LLM节点 —— 多路检索知识库（RAG）+ 严格提示词约束
        """
        messages = state.get("messages", [])
        references = []

        # 1. 提取用户最新问题
        user_query = ""
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                user_query = msg.content
                break

        # 2. 多路检索知识库（RAG核心）- 向量检索 + 关键词检索
        rag_context = ""
        if user_query and self.knowledge_service:
            try:
                search_results = await self.knowledge_service.search_knowledge(
                    query=user_query,
                    limit=5
                )
                if search_results:
                    context_parts = []
                    for idx, result in enumerate(search_results, 1):
                        kp = result.knowledge_point
                        context_parts.append(
                            f"【参考文档{idx}】\n"
                            f"标题: {kp.title}\n"
                            f"课程: {kp.course}\n"
                            f"相似度: {result.score:.2f}\n"
                            f"内容: {kp.content[:800]}{'...' if len(kp.content) > 800 else ''}\n"
                        )
                        references.append({
                            "id": kp.id,
                            "title": kp.title,
                            "source": kp.source_file,
                            "score": round(result.score, 3)
                        })
                    rag_context = "\n\n".join(context_parts)
            except Exception as e:
                print(f"Knowledge search error: {e}")

        # 3. 绝对约束的 prompt
        if rag_context:
            system_prompt_used = f"""你是一个课程学习知识库问答系统的智能助手。

【核心指令-必须绝对遵守】
1. 你只能使用下方【检索到的参考文档】中的信息来回答用户问题
2. 如果参考文档中没有相关问题的答案，你必须直接回答："知识库中未找到与您问题相关的信息，请尝试其他问题或联系教师。"
3. 严禁使用你自身的训练数据中的知识来回答
4. 严禁编造或引用不存在的知识库信息
5. 每个信息点必须在末尾标注来自哪份参考文档

【检索到的参考文档】
{rag_context}

请用中文回答。"""
        else:
            system_prompt_used = FALLBACK_SYSTEM_PROMPT

        try:
            messages_content = [
                {"role": "system", "content": system_prompt_used}
            ]

            # 添加历史对话（排除当前用户问题以防重复）
            for msg in messages:
                if isinstance(msg, HumanMessage) and msg.content == user_query:
                    continue
                if isinstance(msg, HumanMessage):
                    messages_content.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage) and not msg.tool_calls:
                    messages_content.append({"role": "assistant", "content": msg.content})

            # 添加当前用户问题
            messages_content.append({"role": "user", "content": user_query or "你好"})

            response = await self.llm_client.chat(messages_content)
            reply = response.get("choices", [{}])[0].get("message", {}).get("content", "")

            new_messages = list(messages) + [AIMessage(content=reply)]

            return {
                "messages": new_messages,
                "reply": reply,
                "references": references
            }
        except Exception as e:
            error_reply = f"抱歉，系统处理您的请求时出错：{str(e)}"
            new_messages = list(messages) + [AIMessage(content=error_reply)]
            return {
                "messages": new_messages,
                "reply": error_reply,
                "references": references
            }

    async def _tools_node(self, state: AgentState) -> Dict[str, Any]:
        """
        工具节点

        Args:
            state: 当前状态

        Returns:
            Dict: 更新后的状态
        """
        messages = state.get("messages", [])
        references = state.get("references", [])

        if not messages:
            return state

        last_message = messages[-1]
        if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
            return state

        tool_results = []

        for tool_call in last_message.tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})

            try:
                if tool_name == "search_knowledge_tool":
                    result = await self.tool_adapter.search_knowledge(
                        query=tool_args.get("query", ""),
                        course=tool_args.get("course"),
                        limit=tool_args.get("limit", 3)
                    )
                    references.extend(self._extract_references(result))
                elif tool_name == "get_knowledge_detail_tool":
                    result = await self.tool_adapter.get_knowledge_detail(
                        knowledge_id=tool_args.get("knowledge_id", "")
                    )
                elif tool_name == "get_related_knowledge_tool":
                    result = await self.tool_adapter.get_related_knowledge(
                        knowledge_id=tool_args.get("knowledge_id", ""),
                        rel_type=tool_args.get("type", "related")
                    )
                elif tool_name == "get_prerequisites_tool":
                    result = await self.tool_adapter.get_related_knowledge(
                        knowledge_id=tool_args.get("knowledge_id", ""),
                        rel_type="prerequisites"
                    )
                elif tool_name == "get_successors_tool":
                    result = await self.tool_adapter.get_related_knowledge(
                        knowledge_id=tool_args.get("knowledge_id", ""),
                        rel_type="successors"
                    )
                elif tool_name == "record_learning_tool":
                    result = await self.tool_adapter.record_learning(
                        user_id=tool_args.get("user_id", "anonymous"),
                        knowledge_point_id=tool_args.get("knowledge_point_id", ""),
                        action=tool_args.get("action", "view"),
                        duration=tool_args.get("duration", 0)
                    )
                else:
                    result = f"未知工具: {tool_name}"

                tool_results.append(
                    AIMessage(
                        content=str(result),
                        tool_call_id=tool_call.get("id", "")
                    )
                )
            except Exception as e:
                tool_results.append(
                    AIMessage(
                        content=f"工具执行错误: {str(e)}",
                        tool_call_id=tool_call.get("id", "")
                    )
                )

        new_messages = list(messages) + tool_results

        return {
            "messages": new_messages,
            "references": references
        }

    def _extract_references(self, text: str) -> List[str]:
        """
        从文本中提取参考来源

        Args:
            text: 文本内容

        Returns:
            List[str]: 参考来源列表
        """
        import re
        pattern = r'参考来源[:：]\s*([^\n]+)'
        matches = re.findall(pattern, text)
        return matches

    async def process_message(
        self,
        message: str,
        thread_id: str
    ) -> Dict[str, Any]:
        """
        处理用户消息

        Args:
            message: 用户消息
            thread_id: 会话ID

        Returns:
            Dict: 包含回复和参考信息的字典
        """
        config = {"configurable": {"thread_id": thread_id}}

        initial_state = {
            "messages": [HumanMessage(content=message)],
            "references": [],
            "reply": ""
        }

        try:
            result = await self.graph.ainvoke(
                initial_state,
                config=config
            )

            reply = result.get("reply", "")
            references = result.get("references", [])

            if not reply and result.get("messages"):
                for msg in reversed(result["messages"]):
                    if isinstance(msg, AIMessage) and msg.content:
                        reply = msg.content
                        break

            return {
                "reply": reply or "抱歉，未能生成有效回复。",
                "references": references
            }
        except Exception as e:
            return {
                "reply": f"处理消息时出错: {str(e)}",
                "references": []
            }

    async def search_knowledge(
        self,
        query: str
    ) -> Dict[str, Any]:
        """
        直接搜索知识库

        Args:
            query: 查询文本

        Returns:
            Dict: 搜索结果
        """
        results = await self.knowledge_service.search_knowledge(query, limit=3)

        return {
            "results": [r.to_dict() for r in results],
            "count": len(results)
        }
