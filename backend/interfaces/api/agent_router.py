"""
多Agent系统API路由

提供多Agent协同工作的HTTP接口，支持任务查询、工作流执行、状态监控等功能。
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from fastapi.responses import StreamingResponse
import asyncio

from interfaces.schemas.chat_schema import ErrorResponse
from agents import CoordinationAgent
from infrastructure import LLMClient, ChromaKnowledgeRepository
from interfaces.api.auth_router import get_current_user

router = APIRouter(prefix="/api/agents", tags=["多Agent系统"])

# 全局多Agent协调器实例
_coordination_agent: CoordinationAgent = None


def set_coordination_agent(agent: CoordinationAgent):
    """设置协调Agent（由main.py调用）"""
    global _coordination_agent
    _coordination_agent = agent


def get_coordination_agent() -> CoordinationAgent:
    """获取协调Agent"""
    if _coordination_agent is None:
        raise HTTPException(status_code=500, detail="多Agent系统未初始化")
    return _coordination_agent


async def require_authentication(current_user: dict = Depends(get_current_user)):
    """要求用户认证"""
    return current_user


@router.get("/status", responses={401: {"description": "未授权"}})
async def get_agent_status(
    agent: CoordinationAgent = Depends(get_coordination_agent),
    current_user: dict = Depends(require_authentication)
):
    """
    获取多Agent系统状态
    
    返回所有Agent的运行状态和系统健康信息。
    """
    try:
        return agent.get_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", responses={
    401: {"description": "未授权"},
    500: {"model": ErrorResponse, "description": "服务器错误"}
})
async def query_with_multi_agent(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    agent: CoordinationAgent = Depends(get_coordination_agent),
    current_user: dict = Depends(require_authentication)
):
    """
    使用多Agent系统处理查询（同步版本）
    
    执行完整的多Agent工作流：理解→检索→推理→生成→验证→推荐
    
    Args:
        query: 用户查询文本
        context: 可选的上下文信息，如用户级别、课程偏好等
    
    Returns:
        包含答案、引用来源、工作流详情的完整响应
    """
    try:
        result = await agent.execute({
            "query": query,
            "context": context or {}
        })
        
        return {
            "success": result.get("status") == "success",
            "query": result.get("query", query),
            "answer": result.get("answer", ""),
            "citations": result.get("citations", []),
            "confidence": result.get("confidence", 0.0),
            "validation_score": result.get("validation_score", 0.0),
            "validation_feedback": result.get("validation_feedback", ""),
            "related_knowledge": result.get("related_knowledge", []),
            "learning_path": result.get("learning_path", []),
            "workflow_details": result.get("workflow_details", {}),
            "execution_time": result.get("execution_time", 0.0),
            "timestamp": result.get("timestamp", datetime.now().isoformat())
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "多Agent系统处理请求时出错",
                "detail": str(e),
                "code": "AGENT_ERROR"
            }
        )


from pydantic import BaseModel

# 请求模型
class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

@router.post("/query/stream", responses={
    401: {"description": "未授权"},
    500: {"model": ErrorResponse, "description": "服务器错误"}
})
async def query_with_multi_agent_stream(
    request: QueryRequest,
    agent: CoordinationAgent = Depends(get_coordination_agent),
    current_user: dict = Depends(require_authentication)
):
    """
    使用多Agent系统处理查询（流式版本，实时推送工作流状态）
    
    执行完整的多Agent工作流，实时推送每个步骤的执行状态。
    
    Args:
        query: 用户查询文本
        context: 可选的上下文信息，如用户级别、课程偏好等
    
    Returns:
        Server-Sent Events流，包含工作流步骤状态和最终结果
    """
    query = request.query
    context = request.context
    
    async def event_generator():
        # 创建一个队列用于收集步骤状态
        step_queue = asyncio.Queue()
        final_result = None
        error_occurred = None
        
        # 定义步骤回调函数，将状态放入队列
        def step_callback(step_id: str, status: str, details: dict = None):
            step_queue.put_nowait({
                'type': 'step_start' if status == 'running' else 'step_complete',
                'step_id': step_id,
                'status': status,
                'details': details or {},
                'timestamp': datetime.now().isoformat()
            })
        
        # 后台任务：执行工作流
        async def run_workflow():
            nonlocal final_result, error_occurred
            try:
                # 执行工作流，传入回调函数
                final_result = await agent.execute({
                    "query": query,
                    "context": context or {}
                }, step_callback=step_callback)
                # 标记工作流完成
                step_queue.put_nowait({'type': 'workflow_complete'})
            except Exception as e:
                error_occurred = e
                step_queue.put_nowait({
                    'type': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # 启动工作流执行任务
        asyncio.create_task(run_workflow())
        
        # 从队列中获取步骤状态并推送
        while True:
            event = await step_queue.get()
            
            if event['type'] == 'workflow_complete':
                # 工作流完成，推送最终结果
                if final_result:
                    result_data = {
                        'type': 'result',
                        'data': {
                            'success': final_result.get("status") == "success",
                            'query': final_result.get("query", query),
                            'answer': final_result.get("answer", ""),
                            'citations': final_result.get("citations", []),
                            'confidence': final_result.get("confidence", 0.0),
                            'validation_score': final_result.get("validation_score", 0.0),
                            'validation_feedback': final_result.get("validation_feedback", ""),
                            'related_knowledge': final_result.get("related_knowledge", []),
                            'learning_path': final_result.get("learning_path", []),
                            'workflow_details': final_result.get("workflow_details", {}),
                            'execution_time': final_result.get("execution_time", 0.0),
                            'timestamp': final_result.get("timestamp", datetime.now().isoformat())
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(result_data)}\n\n"
                break
            elif event['type'] == 'error':
                # 发生错误
                yield f"data: {json.dumps(event)}\n\n"
                break
            else:
                # 步骤状态更新
                yield f"data: {json.dumps(event)}\n\n"
    
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


@router.post("/workflow/execute/{workflow_id}", responses={
    401: {"description": "未授权"},
    500: {"model": ErrorResponse, "description": "服务器错误"}
})
async def execute_workflow(
    workflow_id: str,
    input_data: Dict[str, Any],
    agent: CoordinationAgent = Depends(get_coordination_agent),
    current_user: dict = Depends(require_authentication)
):
    """
    执行指定的工作流
    
    Args:
        workflow_id: 工作流ID（如 'qa' 表示问答工作流）
        input_data: 工作流输入数据
    
    Returns:
        工作流执行结果
    """
    try:
        # 通过协调Agent执行工作流
        result = await agent.process_query(
            query=input_data.get("query", ""),
            context=input_data.get("context", {})
        )
        
        return {
            "workflow_id": workflow_id,
            "success": result.get("status") == "success",
            "result": result,
            "execution_time": result.get("execution_time", 0.0)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"执行工作流 {workflow_id} 时出错",
                "detail": str(e),
                "code": "WORKFLOW_ERROR"
            }
        )


@router.get("/workflows", responses={401: {"description": "未授权"}})
async def get_registered_workflows(
    agent: CoordinationAgent = Depends(get_coordination_agent),
    current_user: dict = Depends(require_authentication)
):
    """
    获取已注册的工作流列表
    
    Returns:
        工作流ID和描述列表
    """
    try:
        status = agent.get_system_status()
        return {
            "workflows": status.get("workflows", []),
            "description": {
                "qa": "智能问答工作流：理解→检索→推理→生成→验证→推荐"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", responses={401: {"description": "未授权"}})
async def get_task_history(
    limit: int = 10,
    agent: CoordinationAgent = Depends(get_coordination_agent),
    current_user: dict = Depends(require_authentication)
):
    """
    获取最近的任务执行历史
    
    Args:
        limit: 返回的历史记录数量
    
    Returns:
        任务历史列表
    """
    try:
        history = agent.get_task_history(limit=limit)
        return {
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/list", responses={401: {"description": "未授权"}})
async def list_agents(
    agent: CoordinationAgent = Depends(get_coordination_agent),
    current_user: dict = Depends(require_authentication)
):
    """
    获取所有Agent的详细信息
    
    Returns:
        Agent列表及其职责描述
    """
    try:
        status = agent.get_system_status()
        
        agent_descriptions = {
            "understanding": {
                "name": "理解Agent",
                "description": "负责用户意图识别和关键信息提取，分析查询类型和实体",
                "type": "understanding"
            },
            "retrieval": {
                "name": "检索Agent",
                "description": "负责从向量数据库中检索相关知识片段",
                "type": "retrieval"
            },
            "reasoning": {
                "name": "推理Agent",
                "description": "负责基于检索结果进行逻辑推理和综合分析",
                "type": "reasoning"
            },
            "generation": {
                "name": "生成Agent",
                "description": "负责生成最终的自然语言回答",
                "type": "generation"
            },
            "validation": {
                "name": "验证Agent",
                "description": "负责验证答案的准确性和完整性",
                "type": "validation"
            },
            "recommend": {
                "name": "推荐Agent",
                "description": "负责推荐相关知识和学习路径",
                "type": "recommend"
            },
            "coordination": {
                "name": "协调Agent",
                "description": "负责整体协调和任务分配",
                "type": "coordination"
            }
        }
        
        return {
            "agents": [
                {
                    **agent_descriptions.get(agent_id, {"name": agent_id}),
                    "status": status["agents"].get(agent_id, {})
                }
                for agent_id in status["agents"]
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/details", responses={401: {"description": "未授权"}})
async def get_workflow_details(
    agent: CoordinationAgent = Depends(get_coordination_agent),
    current_user: dict = Depends(require_authentication)
):
    """
    获取工作流详细信息
    
    Returns:
        工作流的步骤定义和依赖关系
    """
    workflow_steps = [
        {
            "step": "understanding",
            "name": "理解阶段",
            "agent": "understanding",
            "description": "分析用户查询，识别意图和关键实体",
            "dependencies": [],
            "outputs": ["intent", "question_type", "entities", "keywords"]
        },
        {
            "step": "retrieval",
            "name": "检索阶段",
            "agent": "retrieval",
            "description": "从知识库中检索相关知识片段",
            "dependencies": ["understanding"],
            "outputs": ["knowledge_chunks", "retrieval_metadata"]
        },
        {
            "step": "reasoning",
            "name": "推理阶段",
            "agent": "reasoning",
            "description": "基于检索结果进行逻辑推理",
            "dependencies": ["retrieval"],
            "outputs": ["logical_conclusions", "inferred_info", "perspectives"]
        },
        {
            "step": "generation",
            "name": "生成阶段",
            "agent": "generation",
            "description": "生成最终的自然语言回答",
            "dependencies": ["understanding", "reasoning"],
            "outputs": ["answer", "citations"]
        },
        {
            "step": "validation",
            "name": "验证阶段",
            "agent": "validation",
            "description": "验证答案质量",
            "dependencies": ["generation"],
            "outputs": ["accuracy_score", "completeness_score", "is_valid"]
        },
        {
            "step": "recommend",
            "name": "推荐阶段",
            "agent": "recommend",
            "description": "推荐相关知识和学习路径",
            "dependencies": ["generation"],
            "outputs": ["related_knowledge", "learning_path"]
        }
    ]
    
    return {
        "workflow_name": "智能问答工作流",
        "description": "完整的多Agent智能问答流程",
        "steps": workflow_steps,
        "flow_diagram": "understanding → retrieval → reasoning → generation → validation / recommend"
    }