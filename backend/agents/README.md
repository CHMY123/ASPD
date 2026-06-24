# 多Agent智能问答系统

## 系统概述

基于优化后的知识文档库，构建的多Agent协同智能问答系统，为学生提供准确、全面、个性化的计算机专业知识解答。

## 系统特性

- **多Agent协作**：6个专业Agent协同工作，各司其职
- **知识驱动**：基于向量化的知识库进行检索和推理
- **上下文感知**：理解对话历史，提供连贯的回答
- **个性化推荐**：根据学生水平推荐相关知识
- **可解释性**：提供答案来源和推理过程

## Agent架构

### Agent分类

```
协调Agent (Coordination Agent)
    ├── 理解Agent (Understanding Agent)
    ├── 检索Agent (Retrieval Agent)
    ├── 推理Agent (Reasoning Agent)
    ├── 生成Agent (Generation Agent)
    ├── 验证Agent (Validation Agent)
    └── 推荐Agent (Recommend Agent)
```

### Agent职责

| Agent | 职责 |
|-------|------|
| 协调Agent | 任务分解与分配、Agent间通信协调、工作流控制 |
| 理解Agent | 用户意图识别、关键信息提取、问题分类与路由 |
| 检索Agent | 向量数据库检索、多路召回策略、结果重排序 |
| 推理Agent | 知识推理与综合、逻辑一致性检查、多角度分析 |
| 生成Agent | 答案生成、多样化表达、格式化输出、引用标注 |
| 验证Agent | 答案准确性验证、完整性检查、质量评分 |
| 推荐Agent | 相关知识推荐、学习路径建议、个性化内容推荐 |

## 工作流程

```
用户查询
    ↓
[协调Agent] 任务分解
    ↓
[理解Agent] 意图识别、实体提取
    ↓
[检索Agent] 多路召回、重排序
    ↓
[推理Agent] 知识推理、综合分析
    ↓
[生成Agent] 答案生成、格式化
    ↓
[验证Agent] 质量验证、评分
    ↓
[推荐Agent] 相关推荐、学习路径
    ↓
[协调Agent] 结果聚合
    ↓
返回答案
```

## 文件结构

```
backend/agents/
├── __init__.py           # 包初始化文件
├── base.py               # 基础框架（消息总线、任务调度器等）
├── agents.py             # Agent实现
├── example.py            # 使用示例
└── README.md             # 本文档

docs/
├── knowledge/
│   └── computer_science_optimized.md  # 优化后的知识文档
└── multi_agent_system_architecture.md # 系统架构设计文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install asyncio
```

### 2. 运行示例

```bash
cd backend/agents
python example.py
```

### 3. 交互式使用

选择运行模式中的"交互式模式"，然后输入您的问题。

## 使用方法

### 基本使用

```python
import asyncio
from agents.agents import CoordinationAgent

# 准备知识库
knowledge_base = {
    "knowledge_block_1": {
        "content": "知识内容...",
        "metadata": {
            "章节": "1.1.1",
            "难度": "基础",
            "标签": ["标签1", "标签2"]
        }
    }
}

# 初始化协调Agent
coordination_agent = CoordinationAgent(
    knowledge_base=knowledge_base
)

# 处理查询
async def process_query():
    result = await coordination_agent.process_query(
        query="什么是二叉搜索树？",
        context={
            'user_level': 'intermediate',
            'previous_topics': [],
            'conversation_history': []
        }
    )
    
    print(result['answer'])
    print(f"置信度: {result['confidence']}")

# 运行
asyncio.run(process_query())
```

### 输出格式

```json
{
  "query": "用户查询",
  "answer": "主要答案",
  "citations": [
    {
      "id": 1,
      "knowledge_id": "knowledge_block_6",
      "section": "1.2.2",
      "title": "二叉搜索树",
      "confidence": 0.95
    }
  ],
  "confidence": 0.92,
  "validation_score": 0.88,
  "validation_feedback": "答案质量良好",
  "related_knowledge": [
    {
      "knowledge_id": "knowledge_block_7",
      "section": "1.2.3",
      "title": "AVL树",
      "relevance": 0.85
    }
  ],
  "learning_path": [
    {
      "step": 1,
      "level": "中等",
      "description": "学习中等难度的相关知识",
      "estimated_time": "15分钟"
    }
  ],
  "status": "success",
  "timestamp": "2026-06-23T10:30:00"
}
```

## 知识文档格式

优化后的知识文档采用标准化格式，每个知识块包含：

```markdown
#### 知识块X：标题

---
元数据:
- 章节: X.X.X
- 难度: 基础/中等/较难
- 标签: [标签1, 标签2, ...]
- 预计阅读时间: X分钟
---

**核心概念**
知识点的核心定义

**关键特性**
- 特性1
- 特性2

**详细说明**
详细的解释和说明

**应用场景**
实际应用场景

**相关概念**
相关知识点
```

## 系统扩展

### 添加新Agent

```python
from agents.base import BaseAgent, AgentType

class CustomAgent(BaseAgent):
    def __init__(self, agent_id: str = "custom_agent"):
        super().__init__(agent_id, AgentType.CUSTOM)
    
    async def execute(self, input_data: dict) -> dict:
        # 实现Agent逻辑
        result = {"custom_result": "data"}
        return result

# 注册到协调Agent
coordination_agent.agents['custom'] = CustomAgent()
```

### 自定义工作流

```python
custom_workflow = {
    'name': 'custom_workflow',
    'description': '自定义工作流',
    'steps': {
        'step1': {
            'agent': 'understanding',
            'input_params': {},
            'dependencies': []
        },
        'step2': {
            'agent': 'custom',
            'input_params': {},
            'dependencies': ['step1']
        }
    }
}

coordination_agent.workflow_engine.register_workflow('custom', custom_workflow)
```

## 性能优化

### 并行处理

- 无依赖任务并行执行
- 多Agent实例负载均衡
- 异步I/O操作

### 缓存策略

- 查询结果缓存
- 知识块缓存
- Agent输出缓存

## 监控与调试

### 获取系统状态

```python
status = coordination_agent.get_system_status()
print(status['agents'])      # Agent状态
print(status['tasks'])       # 任务状态
print(status['workflows'])   # 可用工作流
```

### 消息历史

```python
history = coordination_agent.message_bus.get_message_history()
for message in history:
    print(f"{message.sender} -> {message.receiver}: {message.message_type}")
```

## 注意事项

1. **知识库格式**：确保知识库包含content和metadata字段
2. **异步执行**：所有Agent方法都是异步的，需要使用await
3. **错误处理**：系统包含基本的错误处理，但建议添加额外的异常处理
4. **性能考虑**：对于大型知识库，建议使用专业的向量数据库

## 未来改进

- [ ] 集成真实的embedding模型
- [ ] 使用专业的向量数据库（如Milvus、FAISS）
- [ ] 添加更复杂的推理逻辑
- [ ] 支持多轮对话
- [ ] 添加用户反馈机制
- [ ] 实现Agent的持久化和恢复

## 相关文档

- [系统架构设计](../../docs/multi_agent_system_architecture.md)
- [知识文档优化](../../docs/knowledge/computer_science_optimized.md)

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。