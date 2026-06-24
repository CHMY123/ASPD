"""
问答应用服务 (Chat Application Service)

处理问答流程，协调Agent和知识库。
实现基于RAG的智能问答，支持流式输出和多轮对话。
"""

from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime
import logging

from domain.conversation.entity import Conversation, Message
from domain.conversation.repository import ConversationRepository
from domain.knowledge.entity import KnowledgePoint, KnowledgeSearchResult
from infrastructure.agent.graph import AgentGraph

logger = logging.getLogger(__name__)


class ChatService:
    """
    问答应用服务

    协调LangGraph Agent和知识库服务，完成智能问答相关业务操作。

    核心特性：
    1. 多轮对话：支持上下文感知的连续对话
    2. RAG增强：基于检索结果生成回答
    3. 流式输出：支持SSE流式响应
    4. 严格约束：禁止LLM编造知识，必须基于检索结果

    Attributes:
        agent_graph: LangGraph Agent图
        conversation_repo: 会话仓储接口
    """

    # 系统提示词 - 强调必须基于知识库回答
    SYSTEM_PROMPT_KNOWLEDGE = """你是课程学习知识库问答系统的智能助手。

【核心职责】
1. 回答用户关于课程知识的问题
2. 帮助用户理解复杂的概念
3. 提供学习建议和知识推荐

【回答约束-必须严格遵守】
1. 你只能使用【检索到的参考文档】中的信息来回答用户问题
2. 如果参考文档中没有相关信息，你必须直接回答："知识库中未找到与您问题相关的信息，请尝试其他问题或联系教师。"
3. 严禁使用你自身的训练数据中的知识来回答
4. 严禁编造或引用不存在的知识库信息
5. 回答完成后，列出你实际引用的参考来源标题

请用中文回答用户的问题。"""

    SYSTEM_PROMPT_CHAT = """你是一个友好的学习助手。请用中文回答用户的问题，保持简洁清晰。"""

    def __init__(
        self,
        agent_graph: AgentGraph,
        conversation_repo: ConversationRepository
    ):
        """
        初始化问答服务

        Args:
            agent_graph: LangGraph Agent图
            conversation_repo: 会话仓储接口
        """
        self.agent_graph = agent_graph
        self.conversation_repo = conversation_repo

    async def initialize(self) -> None:
        """初始化问答服务"""
        await self.conversation_repo.init_schema()

    async def process_message(
        self,
        message: str,
        thread_id: str,
        user_id: str = "anonymous",
        mode: str = "knowledge"
    ) -> Dict[str, Any]:
        """
        处理用户消息（非流式）

        Args:
            message: 用户消息
            thread_id: 会话ID
            user_id: 用户ID
            mode: 模式（knowledge: 知识检索模式, chat: 普通对话模式）

        Returns:
            Dict: 包含回复和参考信息的字典
        """
        # 获取或创建会话
        conversation = await self._get_or_create_conversation(thread_id, user_id, message)

        # 保存用户消息
        user_msg = Message.user_message(thread_id, message)
        await self.conversation_repo.add_message(user_msg)
        conversation.update_activity()
        await self.conversation_repo.update_conversation(conversation)

        # 根据模式处理
        if mode == "knowledge":
            result = await self._process_knowledge_mode(message)
        else:
            result = await self._process_chat_mode(message)

        # 保存助手回复
        assistant_msg = Message.assistant_message(
            thread_id,
            result["reply"],
            result.get("references", [])
        )
        await self.conversation_repo.add_message(assistant_msg)

        return result

    async def _get_or_create_conversation(
        self,
        thread_id: str,
        user_id: str,
        first_message: str
    ) -> Conversation:
        """获取或创建会话"""
        conversation = await self.conversation_repo.get_conversation(thread_id)

        if not conversation:
            conversation = Conversation(
                id=thread_id,
                user_id=user_id,
                title=first_message[:50] + "..." if len(first_message) > 50 else first_message
            )
            created = await self.conversation_repo.create_conversation(conversation)
            if not created:
                raise RuntimeError(f"创建会话失败: user_id={user_id} 不存在于users表中")

            # 添加系统消息
            system_message = Message.system_message(self.SYSTEM_PROMPT_KNOWLEDGE)
            system_message.conversation_id = thread_id
            await self.conversation_repo.add_message(system_message)

        return conversation

    async def _process_knowledge_mode(self, message: str) -> Dict[str, Any]:
        """
        知识检索模式处理

        完整的RAG流程：
        1. 检索知识库
        2. 构建上下文
        3. 生成回答
        """
        try:
            # RAG检索
            search_results = await self.agent_graph.knowledge_service.search(
                query=message,
                limit=5,
                use_rerank=True
            )

            if not search_results:
                return {
                    "reply": "知识库中未找到与您问题相关的信息，请尝试其他问题或联系教师。",
                    "references": []
                }

            # 构建上下文
            context, references = self.agent_graph.knowledge_service.build_context(
                search_results,
                max_content_length=800
            )

            # 构建提示词
            system_prompt = f"""{self.SYSTEM_PROMPT_KNOWLEDGE}

【检索到的参考文档】
{context}

请基于上述参考文档回答用户问题。"""

            # 调用LLM
            messages_content = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]

            response = await self.agent_graph.llm_client.chat(
                messages_content,
                use_fallback=True
            )

            reply = response.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not reply:
                return {
                    "reply": "抱歉，系统处理您的请求时出错，请稍后重试。",
                    "references": references
                }

            return {
                "reply": reply,
                "references": references
            }

        except Exception as e:
            logger.error(f"Knowledge mode error: {e}")
            return {
                "reply": f"抱歉，系统处理您的请求时出错：{str(e)}",
                "references": []
            }

    async def _process_chat_mode(self, message: str) -> Dict[str, Any]:
        """对话模式处理"""
        try:
            messages_content = [
                {"role": "system", "content": self.SYSTEM_PROMPT_CHAT},
                {"role": "user", "content": message}
            ]

            response = await self.agent_graph.llm_client.chat(
                messages_content,
                use_fallback=True
            )

            reply = response.get("choices", [{}])[0].get("message", {}).get("content", "")

            return {
                "reply": reply or "抱歉，未能生成回复。",
                "references": []
            }

        except Exception as e:
            logger.error(f"Chat mode error: {e}")
            return {
                "reply": f"抱歉，系统处理您的请求时出错：{str(e)}",
                "references": []
            }

    async def process_message_stream(
        self,
        message: str,
        thread_id: str,
        user_id: str = "anonymous",
        mode: str = "knowledge"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式处理用户消息

        完整的RAG流式流程：
        1. 保存用户消息
        2. 检索知识库（获取参考来源）
        3. 流式生成回答

        Yields:
            dict: 事件类型和数据
                  - {"type": "references", "data": [...]}  参考来源
                  - {"type": "token", "data": "..."}       生成 token
                  - {"type": "done", "data": ""}           完成信号
                  - {"type": "error", "data": "..."}       错误信息
        """
        # 1. 获取或创建会话
        conversation = await self._get_or_create_conversation(thread_id, user_id, message)

        # 2. 保存用户消息
        user_msg = Message.user_message(thread_id, message)
        await self.conversation_repo.add_message(user_msg)
        conversation.update_activity()
        await self.conversation_repo.update_conversation(conversation)

        # 3. RAG检索
        rag_context = ""
        references = []

        if mode == "knowledge":
            try:
                search_results = await self.agent_graph.knowledge_service.search(
                    query=message,
                    limit=5,
                    use_rerank=True
                )

                if search_results:
                    rag_context, references = self.agent_graph.knowledge_service.build_context(
                        search_results,
                        max_content_length=800
                    )
            except Exception as e:
                logger.warning(f"Stream RAG search error: {e}")

        # 4. 发送参考来源
        yield {"type": "references", "data": references}

        # 5. 构建提示词
        if rag_context:
            system_prompt = f"""{self.SYSTEM_PROMPT_KNOWLEDGE}

【检索到的参考文档】
{rag_context}

请基于上述参考文档回答用户问题。"""
        else:
            system_prompt = self.SYSTEM_PROMPT_KNOWLEDGE + "\n\n【注意】当前知识库中暂无与您问题相关的参考文档，请明确告知用户。"

        # 6. 流式调用LLM
        messages_content = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]

        full_reply = ""
        try:
            async for token in self.agent_graph.llm_client.chat_stream(messages_content):
                full_reply += token
                yield {"type": "token", "data": token}

            yield {"type": "done", "data": ""}

        except Exception as e:
            logger.error(f"Stream LLM error: {e}")
            yield {"type": "error", "data": str(e)}
            full_reply = f"抱歉，系统处理您的请求时出错：{str(e)}"

        # 7. 保存助手回复
        if full_reply:
            assistant_msg = Message.assistant_message(
                thread_id,
                full_reply,
                references
            )
            await self.conversation_repo.add_message(assistant_msg)

    # ==================== 会话管理 ====================

    async def get_conversation_history(
        self,
        thread_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取会话历史"""
        messages = await self.conversation_repo.get_messages(thread_id, limit)
        return [msg.to_dict() for msg in messages]

    async def get_conversation(self, thread_id: str) -> Optional[Conversation]:
        """获取会话信息"""
        return await self.conversation_repo.get_conversation(thread_id)

    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """获取用户的所有会话"""
        return await self.conversation_repo.get_conversations_by_user(
            user_id, limit, offset
        )

    async def delete_conversation(self, thread_id: str) -> bool:
        """删除会话"""
        await self.conversation_repo.delete_messages(thread_id)
        return await self.conversation_repo.delete_conversation(thread_id)

    async def create_new_conversation(self, user_id: str = "anonymous") -> Conversation:
        """创建新会话"""
        conversation = Conversation(user_id=user_id)
        await self.conversation_repo.create_conversation(conversation)

        system_message = Message.system_message(self.SYSTEM_PROMPT_KNOWLEDGE)
        system_message.conversation_id = conversation.id
        await self.conversation_repo.add_message(system_message)

        return conversation

    async def search_with_context(
        self,
        query: str,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        带上下文的搜索

        利用对话历史增强检索效果
        """
        context_query = query

        if thread_id:
            recent_messages = await self.conversation_repo.get_recent_messages(
                thread_id, count=5
            )
            context = "\n".join([
                f"{msg.role}: {msg.content}"
                for msg in recent_messages
                if msg.role != "system"
            ])
            if context:
                context_query = f"上下文：{context}\n\n当前问题：{query}"

        return await self.agent_graph.search_knowledge(context_query)

    async def get_conversation_stats(self, thread_id: str) -> Dict[str, Any]:
        """获取会话统计"""
        message_count = await self.conversation_repo.count_messages(thread_id)
        conversation = await self.conversation_repo.get_conversation(thread_id)

        return {
            "conversation_id": thread_id,
            "message_count": message_count,
            "created_at": conversation.created_at.isoformat() if conversation else None,
            "updated_at": conversation.updated_at.isoformat() if conversation else None,
        }
