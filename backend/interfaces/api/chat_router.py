"""
问答API路由

处理问答相关的HTTP请求。
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from typing import List, TYPE_CHECKING
import json
import logging
import time as _time
import sys

if TYPE_CHECKING:
    from agents.agents import CoordinationAgent

from interfaces.schemas.chat_schema import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    MessageResponse,
    ErrorResponse,
)
from application.chat_service import ChatService
from interfaces.api.auth_router import get_current_user

logger = logging.getLogger(__name__)

# 强制输出调试信息到 stdout
def debug_print(msg: str):
    """强制输出调试信息（stdout + stderr 双写）"""
    text = f"[CHAT] {msg}"
    print(text, flush=True, file=sys.stdout)
    print(text, flush=True, file=sys.stderr)

router = APIRouter(prefix="/api/chat", tags=["问答"])

_chat_service: ChatService = None
_coordination_agent: 'CoordinationAgent' = None  # 多Agent协调器


def set_coordination_agent(agent: 'CoordinationAgent'):
    """设置多Agent协调器（由main.py调用）"""
    global _coordination_agent
    _coordination_agent = agent


def get_coordination_agent() -> 'CoordinationAgent':
    """获取多Agent协调器"""
    if _coordination_agent is None:
        raise HTTPException(status_code=500, detail="多Agent系统未初始化")
    return _coordination_agent


def set_chat_service(service: ChatService):
    """设置聊天服务（由main.py调用）"""
    global _chat_service
    _chat_service = service


def get_chat_service() -> ChatService:
    """获取聊天服务"""
    if _chat_service is None:
        raise HTTPException(status_code=500, detail="聊天服务未初始化")
    return _chat_service


async def require_authentication(current_user: dict = Depends(get_current_user)):
    """要求用户认证"""
    return current_user


@router.post(
    "",
    response_model=ChatResponse,
    responses={
        401: {"description": "未授权"},
        500: {"model": ErrorResponse, "description": "服务器错误"}
    }
)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
    current_user: dict = Depends(require_authentication)
):
    """
    处理用户的自然语言问答请求

    支持单轮和多轮对话，基于知识库检索和大语言模型生成回答。
    """
    try:
        result = await service.process_message(
            message=request.message,
            thread_id=request.thread_id,
            user_id=current_user.get("id") if not request.user_id or request.user_id == "anonymous" else request.user_id
        )

        return ChatResponse(
            reply=result["reply"],
            references=result.get("references", [])
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "抱歉，系统处理您的请求时出错，请稍后重试。",
                "detail": str(e),
                "code": "CHAT_ERROR"
            }
        )


@router.get(
    "/{thread_id}/history",
    response_model=List[MessageResponse],
    responses={401: {"description": "未授权"}}
)
async def get_chat_history(
    thread_id: str,
    limit: int = 50,
    service: ChatService = Depends(get_chat_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取会话历史消息

    返回指定会话的所有消息记录。
    """
    try:
        messages = await service.get_conversation_history(
            thread_id=thread_id,
            limit=limit
        )
        # 安全转换references - 确保id为字符串类型（修复Terminal#993-1011报错）
        result = []
        for msg in messages:
            refs = msg.get("references", [])
            if not isinstance(refs, list):
                refs = []
            
            # 确保每个reference的id都是字符串类型
            safe_refs = []
            for ref in refs:
                if isinstance(ref, dict):
                    # 确保id字段存在且为字符串
                    if 'id' in ref:
                        ref['id'] = str(ref['id'])
                    safe_refs.append(ref)
            
            msg["references"] = safe_refs
            result.append(MessageResponse(**msg))
        return result
    except Exception as e:
        import traceback
        logger.error(f"获取会话历史错误: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/my",
    response_model=List[ConversationResponse],
    responses={401: {"description": "未授权"}}
)
async def get_my_conversations(
    limit: int = 20,
    offset: int = 0,
    service: ChatService = Depends(get_chat_service),
    current_user: dict = Depends(require_authentication)
):
    """获取当前登录用户的所有会话"""
    try:
        conversations = await service.get_user_conversations(
            user_id=current_user.get("id"),
            limit=limit,
            offset=offset
        )
        return [
            ConversationResponse(
                id=c.id,
                user_id=c.user_id,
                title=c.title,
                message_count=c.message_count,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in conversations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{thread_id}",
    response_model=ConversationResponse,
    responses={401: {"description": "未授权"}}
)
async def get_conversation(
    thread_id: str,
    service: ChatService = Depends(get_chat_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取会话信息

    返回指定会话的基本信息。
    """
    try:
        conversation = await service.get_conversation(thread_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="会话不存在")

        return ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            message_count=conversation.message_count,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/user/{user_id}",
    response_model=List[ConversationResponse],
    responses={401: {"description": "未授权"}}
)
async def get_user_conversations(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    service: ChatService = Depends(get_chat_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取用户的所有会话

    返回指定用户创建的会话列表。
    """
    try:
        conversations = await service.get_user_conversations(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        return [
            ConversationResponse(
                id=c.id,
                user_id=c.user_id,
                title=c.title,
                message_count=c.message_count,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in conversations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{thread_id}", responses={401: {"description": "未授权"}})
async def delete_conversation(
    thread_id: str,
    service: ChatService = Depends(get_chat_service),
    current_user: dict = Depends(require_authentication)
):
    """
    删除会话

    删除指定会话及其所有消息。
    """
    try:
        success = await service.delete_conversation(thread_id)
        if not success:
            raise HTTPException(status_code=404, detail="会话不存在")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/new", responses={401: {"description": "未授权"}})
async def create_new_conversation(
    user_id: str = "anonymous",
    service: ChatService = Depends(get_chat_service),
    current_user: dict = Depends(require_authentication)
):
    """
    创建新会话

    创建一个新的空会话，返回会话信息。
    """
    try:
        conversation = await service.create_new_conversation(user_id)
        return {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "title": conversation.title
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/knowledge",
    responses={
        401: {"description": "未授权"},
        500: {"model": ErrorResponse, "description": "服务器错误"}
    }
)
async def chat_knowledge(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
    current_user: dict = Depends(require_authentication)
):
    """
    知识检索模式问答

    基于课程知识库进行检索增强生成，提供精准的专业知识解答。
    """
    try:
        result = await service.process_message(
            message=request.message,
            thread_id=request.thread_id,
            user_id=current_user.get("id") if not request.user_id or request.user_id == "anonymous" else request.user_id,
            mode="knowledge"
        )

        return {
            "response": result.get("reply", "暂无相关知识"),
            "references": result.get("references", []),
            "agent": "知识讲解Agent",
            "reasoning": result.get("reasoning")
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "抱歉，系统处理您的请求时出错，请稍后重试。",
                "detail": str(e),
                "code": "KNOWLEDGE_ERROR"
            }
        )


@router.post(
    "/knowledge/stream",
    responses={
        401: {"description": "未授权"},
        500: {"description": "服务器错误"}
    }
)
async def chat_knowledge_stream(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
    current_user: dict = Depends(require_authentication)
):
    """
    知识检索模式问答（流式输出SSE）

    基于课程知识库进行检索增强生成，以流式方式返回回复。
    使用 Server-Sent Events 协议。
    """
    user_id = current_user.get("id") if not request.user_id or request.user_id == "anonymous" else request.user_id

    async def event_generator():
        try:
            async for event in service.process_message_stream(
                message=request.message,
                thread_id=request.thread_id,
                user_id=user_id,
                mode="knowledge"
            ):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
    )


@router.post(
    "/message",
    responses={
        401: {"description": "未授权"},
        500: {"model": ErrorResponse, "description": "服务器错误"}
    }
)
async def chat_message(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
    current_user: dict = Depends(require_authentication)
):
    """
    普通对话模式

    支持开放域对话交流，直接使用大语言模型进行回答。
    """
    try:
        result = await service.process_message(
            message=request.message,
            thread_id=request.thread_id,
            user_id=current_user.get("id") if not request.user_id or request.user_id == "anonymous" else request.user_id,
            mode="chat"
        )

        return {
            "response": result.get("reply", "暂无回答"),
            "agent": None
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "抱歉，系统处理您的请求时出错，请稍后重试。",
                "detail": str(e),
                "code": "CHAT_ERROR"
            }
        )


@router.post(
    "/multi-agent",
    responses={
        401: {"description": "未授权"},
        500: {"model": ErrorResponse, "description": "服务器错误"}
    }
)
async def chat_multi_agent(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
    current_user: dict = Depends(require_authentication)
):
    """
    多Agent协同对话模式

    执行完整的多Agent工作流：理解→检索→推理→生成→验证→推荐
    返回包含工作流详情的完整响应。
    """
    debug_print("=" * 80)
    debug_print("【多Agent协同对话请求开始】")
    debug_print("=" * 80)
    
    try:
        # 1. 获取协调Agent
        debug_print("步骤1: 获取CoordinationAgent实例...")
        agent = get_coordination_agent()
        debug_print(f"  CoordinationAgent获取成功: {type(agent).__name__}")
        debug_print(f"  Agent内部组件: {list(agent.agents.keys())}")
        
        # 2. 确定用户ID
        user_id = current_user.get("id") if not request.user_id or request.user_id == "anonymous" else request.user_id
        debug_print(f"步骤2: 用户ID确定: {user_id}")
        debug_print(f"  request.user_id: {request.user_id}")
        debug_print(f"  current_user.id: {current_user.get('id')}")
        
        # 3. 记录请求信息
        debug_print(f"步骤3: 请求信息:")
        debug_print(f"  消息内容: '{request.message[:100]}{'...' if len(request.message) > 100 else ''}'")
        debug_print(f"  消息长度: {len(request.message)} 字符")
        debug_print(f"  thread_id: {request.thread_id}")
        
        # 4. 调用多Agent处理
        debug_print("步骤4: 调用agent.process_query()...")
        _start = _time.time()
        
        result = await agent.process_query(
            query=request.message,
            context={
                "user_id": user_id,
                "user_level": "intermediate",
                "mode": "multi_agent"
            }
        )
        
        _elapsed = _time.time() - _start
        debug_print(f"  process_query()完成，耗时: {_elapsed:.2f}秒")
        
        # 5. 详细分析返回结果
        debug_print("步骤5: 分析返回结果...")
        debug_print(f"  result类型: {type(result).__name__}")
        debug_print(f"  result.keys: {list(result.keys())}")
        
        # 分析工作流详情
        workflow_details = result.get("workflow_details", {})
        debug_print(f"  workflow_details.keys: {list(workflow_details.keys())}")
        
        for step_name, step_info in workflow_details.items():
            debug_print(f"    [{step_name}]:")
            debug_print(f"      status: {step_info.get('status')}")
            if step_name == "understanding":
                debug_print(f"      intent: {step_info.get('intent')}")
                debug_print(f"      requires_database_query: {step_info.get('requires_database_query')}")
                debug_print(f"      requires_knowledge_base_search: {step_info.get('requires_knowledge_base_search')}")
                debug_print(f"      entities: {step_info.get('entities')}")
            elif step_name == "retrieval":
                debug_print(f"      knowledge_count: {step_info.get('knowledge_count')}")
                debug_print(f"      has_real_data: {step_info.get('has_real_data')}")
                debug_print(f"      data_source_distribution: {step_info.get('data_source_distribution')}")
                chunks_summary = step_info.get('knowledge_chunks_summary', [])
                for i, chunk in enumerate(chunks_summary[:3]):
                    debug_print(f"        chunk[{i+1}]: knowledge_id={chunk.get('knowledge_id')}, data_source={chunk.get('data_source')}, is_real={chunk.get('is_real_data')}")
            elif step_name == "generation":
                debug_print(f"      answer_length: {step_info.get('answer_length')}")
                debug_print(f"      has_real_data: {step_info.get('has_real_data')}")
            elif step_name == "validation":
                debug_print(f"      overall_score: {step_info.get('overall_score')}")
                debug_print(f"      feedback: {step_info.get('feedback')}")
        
        # 分析答案
        answer = result.get("answer", "")
        debug_print(f"  答案长度: {len(answer)} 字符")
        debug_print(f"  答案前200字符: '{answer[:200]}{'...' if len(answer) > 200 else ''}'")
        
        # 分析引用
        citations = result.get("citations", [])
        debug_print(f"  引用数量: {len(citations)}")
        for i, citation in enumerate(citations[:5]):
            debug_print(f"    citation[{i+1}]: knowledge_id={citation.get('knowledge_id')}, data_source={citation.get('data_source')}, is_real={citation.get('is_real_data')}, warning={citation.get('warning')}")
        
        # 分析调试信息
        debug_info = result.get("debug_info", {})
        debug_print(f"  debug_info: {debug_info}")
        
        # 检查是否有真实数据警告
        if debug_info.get("warning"):
            debug_print(f"  ⚠️ 警告: {debug_info.get('warning')}")
        
        # 6. 保存会话数据
        debug_print("步骤6: 保存会话数据...")
        thread_id = request.thread_id or request.message[:32]
        debug_print(f"  使用thread_id: {thread_id}")
        
        # 获取或创建会话
        conversation = await service._get_or_create_conversation(thread_id, user_id, request.message)
        debug_print(f"  会话创建/获取成功: {conversation.id}")
        
        # 保存用户消息
        from domain.conversation.entity import Message
        user_msg = Message.user_message(thread_id, request.message)
        await service.conversation_repo.add_message(user_msg)
        debug_print(f"  用户消息已保存")
        
        conversation.update_activity()
        await service.conversation_repo.update_conversation(conversation)
        
        # 保存助手回复
        assistant_msg = Message.assistant_message(
            thread_id,
            result.get("answer", "暂无回答"),
            result.get("citations", []),
            agent_used="多Agent协同系统",
            workflow_details=workflow_details
        )
        msg_saved = await service.conversation_repo.add_message(assistant_msg)
        debug_print(f"  助手消息已保存: {msg_saved}")
        
        # 7. 构建返回响应
        debug_print("步骤7: 构建返回响应...")
        response_data = {
            "response": result.get("answer", "暂无回答"),
            "references": result.get("citations", []),
            "agent": "多Agent协同系统",
            "workflow_details": workflow_details,
            "confidence": result.get("confidence", 0.0),
            "validation_score": result.get("validation_score", 0.0),
            "related_knowledge": result.get("related_knowledge", []),
            "learning_path": result.get("learning_path", []),
            "execution_time": result.get("execution_time", 0.0),
            "thread_id": thread_id,
            "debug_info": debug_info  # 添加调试信息到响应
        }
        
        debug_print("=" * 80)
        debug_print("【多Agent协同对话请求完成】")
        debug_print(f"总耗时: {_elapsed:.2f}秒")
        debug_print(f"返回响应keys: {list(response_data.keys())}")
        debug_print("=" * 80)
        
        return response_data
        
    except Exception as e:
        debug_print(f"❌ 多Agent协同对话错误: {e}")
        import traceback
        debug_print(f"错误堆栈:\n{traceback.format_exc()}")
        logger.error(f"多Agent协同对话错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "多Agent系统处理请求时出错",
                "detail": str(e),
                "code": "MULTI_AGENT_ERROR"
            }
        )


@router.get("/{thread_id}/stats", responses={401: {"description": "未授权"}})
async def get_conversation_stats(
    thread_id: str,
    service: ChatService = Depends(get_chat_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取会话统计

    返回指定会话的统计信息。
    """
    try:
        stats = await service.get_conversation_stats(thread_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
