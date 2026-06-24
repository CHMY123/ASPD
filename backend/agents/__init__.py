"""
多Agent智能问答系统
"""

from .base import (
    AgentType,
    MessageType,
    AgentMessage,
    Task,
    BaseAgent,
    MessageBus,
    TaskScheduler,
    WorkflowEngine
)

from .agents import (
    UnderstandingAgent,
    RetrievalAgent,
    ReasoningAgent,
    GenerationAgent,
    ValidationAgent,
    RecommendAgent,
    CoordinationAgent
)

__version__ = "1.0.0"
__author__ = "AI System Team"

__all__ = [
    # 基础框架
    'AgentType',
    'MessageType',
    'AgentMessage',
    'Task',
    'BaseAgent',
    'MessageBus',
    'TaskScheduler',
    'WorkflowEngine',
    
    # Agent实现
    'UnderstandingAgent',
    'RetrievalAgent',
    'ReasoningAgent',
    'GenerationAgent',
    'ValidationAgent',
    'RecommendAgent',
    'CoordinationAgent'
]