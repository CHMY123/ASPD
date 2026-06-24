"""
多Agent智能问答系统 - 基础框架
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import asyncio
import uuid
import json
import logging

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Agent类型枚举"""
    COORDINATION = "coordination"
    UNDERSTANDING = "understanding"
    RETRIEVAL = "retrieval"
    REASONING = "reasoning"
    GENERATION = "generation"
    VALIDATION = "validation"
    RECOMMEND = "recommend"


class MessageType(Enum):
    """消息类型枚举"""
    TASK = "task"
    RESULT = "result"
    ERROR = "error"
    CONTROL = "control"


@dataclass
class AgentMessage:
    """Agent间通信消息"""
    sender: str
    receiver: str
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: int = 0
    retry_count: int = 0
    timeout: int = 30


@dataclass
class Task:
    """任务定义"""
    id: str
    agent: str
    input: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, agent_id: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.message_queue = asyncio.Queue()
        self.running = False
        
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行Agent任务"""
        pass
    
    async def start(self):
        """启动Agent"""
        self.running = True
        await self._process_messages()
    
    async def stop(self):
        """停止Agent"""
        self.running = False
    
    async def _process_messages(self):
        """处理消息队列"""
        while self.running:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                await self._handle_message(message)
            except asyncio.TimeoutError:
                continue
    
    async def _handle_message(self, message: AgentMessage):
        """处理接收到的消息"""
        try:
            if message.message_type == MessageType.TASK:
                result = await self.execute(message.payload)
                await self._send_result(message, result)
            elif message.message_type == MessageType.CONTROL:
                await self._handle_control(message)
        except Exception as e:
            await self._send_error(message, str(e))
    
    async def _send_result(self, original_message: AgentMessage, result: Dict[str, Any]):
        """发送结果消息"""
        # 这里应该通过消息总线发送，简化实现
        pass
    
    async def _send_error(self, original_message: AgentMessage, error: str):
        """发送错误消息"""
        # 这里应该通过消息总线发送，简化实现
        pass
    
    async def _handle_control(self, message: AgentMessage):
        """处理控制消息"""
        command = message.payload.get('command')
        if command == 'stop':
            await self.stop()
    
    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type.value,
            'running': self.running,
            'queue_size': self.message_queue.qsize()
        }


class MessageBus:
    """消息总线，负责Agent间通信"""
    
    def __init__(self):
        self.queues: Dict[str, asyncio.Queue] = {}
        self.subscribers: Dict[str, List[str]] = {}
        self.message_history: List[AgentMessage] = []
        self.agents: Dict[str, BaseAgent] = {}  # 存储Agent实例
    
    def register_agent(self, agent_id: str, agent_instance: BaseAgent = None):
        """注册Agent"""
        if agent_id not in self.queues:
            self.queues[agent_id] = asyncio.Queue()
        if agent_instance:
            self.agents[agent_id] = agent_instance
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """获取Agent实例"""
        return self.agents.get(agent_id)
    
    def subscribe(self, agent_id: str, message_type: MessageType):
        """订阅消息类型"""
        if message_type.value not in self.subscribers:
            self.subscribers[message_type.value] = []
        self.subscribers[message_type.value].append(agent_id)
    
    async def send(self, message: AgentMessage):
        """发送消息"""
        self.message_history.append(message)
        
        if message.receiver in self.queues:
            await self.queues[message.receiver].put(message)
        else:
            raise ValueError(f"Agent {message.receiver} not registered")
    
    async def broadcast(self, message: AgentMessage, receivers: List[str]):
        """广播消息"""
        for receiver in receivers:
            message_copy = AgentMessage(
                sender=message.sender,
                receiver=receiver,
                message_type=message.message_type,
                payload=message.payload.copy(),
                timestamp=message.timestamp,
                correlation_id=message.correlation_id,
                priority=message.priority,
                timeout=message.timeout
            )
            await self.send(message_copy)
    
    async def receive(self, agent_id: str, timeout: float = 30.0) -> Optional[AgentMessage]:
        """接收消息"""
        if agent_id not in self.queues:
            return None
        
        try:
            return await asyncio.wait_for(
                self.queues[agent_id].get(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            return None
    
    def get_message_history(self, agent_id: Optional[str] = None) -> List[AgentMessage]:
        """获取消息历史"""
        if agent_id:
            return [msg for msg in self.message_history 
                   if msg.sender == agent_id or msg.receiver == agent_id]
        return self.message_history.copy()


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.failed_tasks: Dict[str, Task] = {}
    
    async def schedule(self, tasks: List[Task]):
        """调度任务执行"""
        # 1. 构建依赖图
        dependency_graph = self._build_dependency_graph(tasks)
        
        # 2. 拓扑排序
        execution_order = self._topological_sort(dependency_graph)
        
        # 3. 构建任务ID到任务对象的映射
        task_map = {task.id: task for task in tasks}
        
        # 4. 按层级执行
        for level in execution_order:
            await asyncio.gather(*[
                self._execute_task(task_map[task_id])
                for task_id in level
            ])
    
    async def schedule_with_data_flow(self, tasks: List[Task]):
        """调度任务执行（包含数据传递）"""
        # 1. 构建依赖图
        dependency_graph = self._build_dependency_graph(tasks)
        
        # 2. 拓扑排序
        execution_order = self._topological_sort(dependency_graph)
        
        # 3. 构建任务ID到任务对象的映射
        task_map = {task.id: task for task in tasks}
        
        # 4. Agent ID 到输出 key 的映射表
        AGENT_OUTPUT_KEY_MAP = {
            'understanding': 'understanding_result',
            'retrieval': 'retrieval_result',
            'reasoning': 'reasoning_result',
            'generation': 'generation_result',
            'validation': 'validation_result',
            'recommend': 'recommend_result',
        }
        
        # 5. 按层级执行（正确传递依赖任务的输出到对应的 input key）
        for level in execution_order:
            # 为当前层级的任务注入依赖任务的输出
            for task_id in level:
                task = task_map[task_id]
                # 收集所有依赖任务的输出，映射到正确的 key 名
                for dep_id in task.dependencies:
                    if dep_id in self.completed_tasks:
                        dep_task = self.completed_tasks[dep_id]
                        dep_output = dep_task.output if dep_task.output else {}
                        
                        # 从 dep_id 中提取前缀（如 "understanding" 从 "understanding" 中提取）
                        dep_prefix = dep_id.split('_')[0] if '_' in dep_id else dep_id
                        target_key = AGENT_OUTPUT_KEY_MAP.get(dep_prefix, f"{dep_id}_result")
                        
                        # 将所有依赖输出注入到正确命名的 key 中
                        task.input[target_key] = dep_output
                        # 也保留原始兼容 key
                        task.input[f"{dep_id}_result"] = dep_output
                    elif dep_id in self.failed_tasks:
                        # 依赖任务失败，记录错误但仍继续执行（让下游任务自行处理缺失数据）
                        logger.warning(f"[TaskScheduler] 依赖任务 {dep_id} 失败，{task.id} 将使用不完整的数据继续执行")
            
            # 并行执行当前层级的任务（错误隔离：一个任务失败不影响同层级其他任务）
            level_tasks = []
            for task_id in level:
                level_tasks.append(self._execute_task(task_map[task_id]))
            
            await asyncio.gather(*level_tasks, return_exceptions=True)
            
            # 记录当前层级执行结果
            for task_id in level:
                task = task_map[task_id]
                if task.status == 'failed':
                    logger.warning(f"[TaskScheduler] 任务 {task_id} 执行失败: {task.error}")
                else:
                    logger.debug(f"[TaskScheduler] 任务 {task_id} 执行成功")
    
    def _build_dependency_graph(self, tasks: List[Task]) -> Dict[str, List[str]]:
        """构建依赖图"""
        graph = {task.id: task.dependencies for task in tasks}
        return graph
    
    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """拓扑排序，返回执行层级"""
        in_degree = {node: 0 for node in graph}
        
        for node in graph:
            for dependency in graph[node]:
                if dependency in in_degree:
                    in_degree[node] += 1
        
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current_level = queue.copy()
            queue.clear()
            result.append(current_level)
            
            for node in current_level:
                for neighbor, deps in graph.items():
                    if node in deps:
                        in_degree[neighbor] -= 1
                        if in_degree[neighbor] == 0:
                            queue.append(neighbor)
        
        return result
    
    async def _execute_task(self, task: Task, max_retries: int = 2):
        """执行单个任务（带重试机制）"""
        self.running_tasks[task.id] = task
        task.status = "running"
        
        last_error = None
        for attempt in range(max_retries):
            try:
                # 获取Agent实例并执行
                agent_instance = self.message_bus.get_agent(task.agent)
                if agent_instance:
                    # 直接调用Agent的execute方法
                    task.output = await agent_instance.execute(task.input)
                    task.status = "completed"
                    self.completed_tasks[task.id] = task
                    return
                else:
                    raise Exception(f"Agent {task.agent} not found")
                    
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    logger.warning(f"[TaskScheduler] 任务 {task.id} 第{attempt+1}次尝试失败，即将重试: {last_error[:100]}")
                    await asyncio.sleep(0.5 * (attempt + 1))  # 递增延迟
                else:
                    logger.error(f"[TaskScheduler] 任务 {task.id} 重试{max_retries}次后仍失败: {last_error}")
        
        # 所有重试均失败
        task.error = last_error
        task.status = "failed"
        self.failed_tasks[task.id] = task
        if task.id in self.running_tasks:
            del self.running_tasks[task.id]
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        for task_dict in [self.running_tasks, self.completed_tasks, self.failed_tasks]:
            if task_id in task_dict:
                task = task_dict[task_id]
                return {
                    'id': task.id,
                    'status': task.status,
                    'output': task.output,
                    'error': task.error
                }
        return None
    
    def get_all_tasks(self) -> Dict[str, Any]:
        """获取所有任务状态"""
        return {
            'running': {k: v.status for k, v in self.running_tasks.items()},
            'completed': list(self.completed_tasks.keys()),
            'failed': list(self.failed_tasks.keys())
        }


class WorkflowEngine:
    """工作流引擎"""
    
    def __init__(self, message_bus: MessageBus, scheduler: TaskScheduler):
        self.message_bus = message_bus
        self.scheduler = scheduler
        self.workflows: Dict[str, Dict] = {}
    
    def register_workflow(self, workflow_id: str, workflow_config: Dict):
        """注册工作流"""
        self.workflows[workflow_id] = workflow_config
    
    async def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行工作流"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        logger.info(f"[WorkflowEngine] 开始执行工作流: {workflow_id}, 步骤数={len(workflow.get('steps', {}))}")
        
        # 1. 生成任务
        tasks = self._generate_tasks(workflow, input_data)
        logger.debug(f"[WorkflowEngine] 生成{len(tasks)}个任务: {[t.id for t in tasks]}")
        
        # 2. 调度执行（包含数据传递）
        import time as _time
        _start = _time.time()
        await self.scheduler.schedule_with_data_flow(tasks)
        _elapsed = _time.time() - _start
        logger.info(f"[WorkflowEngine] 工作流执行完成: 耗时={_elapsed:.2f}s")
        
        # 3. 收集结果
        return self._collect_results(tasks)
    
    def _generate_tasks(self, workflow: Dict, input_data: Dict[str, Any]) -> List[Task]:
        """生成任务列表"""
        tasks = []
        
        for step_id, step_config in workflow['steps'].items():
            task = Task(
                id=step_id,
                agent=step_config['agent'],
                input={
                    **input_data,
                    **step_config.get('input_params', {})
                },
                dependencies=step_config.get('dependencies', [])
            )
            tasks.append(task)
        
        return tasks
    
    def _collect_results(self, tasks: List[Task]) -> Dict[str, Any]:
        """收集任务结果"""
        results = {}
        
        for task in tasks:
            status = self.scheduler.get_task_status(task.id)
            if status:
                results[task.id] = status
        
        return results


# 导出主要类
__all__ = [
    'AgentType',
    'MessageType',
    'AgentMessage',
    'Task',
    'BaseAgent',
    'MessageBus',
    'TaskScheduler',
    'WorkflowEngine'
]