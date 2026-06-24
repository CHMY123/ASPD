# 华南师范大学计算机专业课程管理系统 - 技术架构文档

## 一、架构概述

### 1.1 系统定位

本系统是一个面向华南师范大学计算机专业学生的课程管理系统，采用领域驱动设计（DDD）分层架构，结合检索增强生成（RAG）技术和多智能体协同机制，提供课程信息管理、电子资源访问、智能知识检索及多智能体协同对话等功能。

### 1.2 架构原则

- **分层架构**：采用DDD四层架构，职责清晰
- **松耦合**：模块间通过接口通信，降低依赖
- **可扩展**：支持功能模块的灵活扩展
- **高性能**：通过向量数据库和缓存提升检索效率

## 二、系统架构

### 2.1 分层架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      接口层 (Interfaces)                       │
│  ├── REST API (FastAPI)                                       │
│  ├── SSE (Server-Sent Events)                                  │
│  └── Vue3前端                                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      应用层 (Application)                       │
│  ├── AuthService          │  ChatService                       │
│  ├── CourseService        │  BookService                       │
│  ├── KnowledgeService     │  LearningService                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                        领域层 (Domain)                         │
│  ├── User         │  Course        │  Conversation            │
│  ├── Knowledge    │  Book          │  LearningRecord          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                   基础设施层 (Infrastructure)                  │
│  ├── TiDB Cloud          │  Chroma Vector DB                  │
│  ├── LangGraph Agent     │  LLM Client                       │
│  └── File Storage        │  Storage Service                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 分层职责说明

| 层次 | 职责 | 核心组件 |
|------|------|---------|
| 接口层 | 处理HTTP请求，提供前端界面 | FastAPI、Vue3、SSE |
| 应用层 | 编排业务用例，协调领域对象 | 各业务Service |
| 领域层 | 定义业务实体和业务规则 | 实体类、仓储接口 |
| 基础设施层 | 实现技术细节，提供外部服务 | 数据库、LLM、文件存储 |

### 2.3 项目目录结构

```
backend/
├── main.py                  # FastAPI入口
├── config.py                # 配置管理（从.env读取）
├── demo.py                   # RAG示例代码
│
├── agents/                   # Agent模块
│   ├── agents.py             # Agent实现
│   └── base.py               # Agent基类
│
├── application/             # 应用层
│   ├── auth_service.py       # 认证服务
│   ├── chat_service.py        # 问答服务
│   ├── knowledge_service.py  # 知识库服务
│   └── learning_service.py   # 学习服务
│
├── infrastructure/           # 基础设施层
│   ├── database.py           # 数据库连接池
│   ├── database_init.py      # 数据库初始化
│   ├── llm_client.py         # LLM/Embedding/Rerank封装
│   ├── knowledge_repository.py  # Chroma向量库实现
│   ├── conversation_repository.py  # 会话仓储
│   ├── learning_repository.py # 学习记录仓储
│   ├── user_repository.py    # 用户仓储
│   ├── storage_service.py    # 文件存储服务
│   └── agent/
│       ├── graph.py          # Agent编排图
│       └── tools.py          # Agent工具
│
├── interfaces/              # 接口层
│   ├── api/
│   │   ├── auth_router.py    # 认证接口
│   │   ├── chat_router.py    # 问答接口
│   │   ├── knowledge_router.py  # 知识库接口
│   │   ├── learning_router.py  # 学习接口
│   │   ├── upload_router.py   # 上传接口
│   │   └── agent_router.py   # Agent接口
│   └── schemas/
│       ├── chat_schema.py
│       ├── knowledge_schema.py
│       └── learning_schema.py
│
├── domain/                  # 领域层
│   ├── user/
│   ├── knowledge/
│   ├── conversation/
│   └── learning/
│
├── common/                  # 公共模块
│   ├── exceptions.py
│   ├── logger.py
│   └── validators.py
│
├── tests/                   # 单元测试
│   ├── test_auth_service.py
│   ├── test_knowledge_service.py
│   ├── test_llm_client.py
│   └── test_validators.py
│
├── db/                      # 数据库脚本
│   └── init.sql
│
└── cs_know_db/              # Chroma向量数据库
```

## 三、多智能体架构设计

### 3.1 Agent架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     Coordination Agent                          │
│  ├── 请求接收与意图分析                                         │
│  ├── Agent路由决策                                             │
│  └── 结果汇总与响应生成                                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Understanding │   │   Retrieval   │   │  Generation   │
│     Agent     │──▶│    Agent      │──▶│    Agent      │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        │                   │                   ▼
        │                   │         ┌───────────────┐
        │                   │         │  Validation   │
        │                   │         │    Agent      │
        │                   │         └───────────────┘
        │                   │
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│   Reasoning   │   │  Recommend    │
│    Agent      │   │    Agent      │
└───────────────┘   └───────────────┘
```

### 3.2 Agent职责定义

| Agent名称 | 职责描述 | 核心能力 |
|-----------|---------|---------|
| Coordination Agent | 任务协调、流程控制 | 任务调度、Agent编排 |
| Understanding Agent | 用户意图识别、关键信息提取 | 实体识别、意图分类 |
| Retrieval Agent | 知识检索、数据库查询 | 向量检索、关键词检索、RRF融合 |
| Reasoning Agent | 知识推理与综合 | 逻辑推理、多角度分析 |
| Generation Agent | 答案生成、格式化输出 | 流式生成、引用标注 |
| Validation Agent | 答案质量验证 | 准确性检查、质量评分 |
| Recommend Agent | 相关内容推荐 | 知识推荐、学习路径 |

### 3.3 Agent协作流程

```
用户问题
    │
    ▼
┌─────────────────┐
│ Coordination    │
│    Agent        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Understanding  │────▶│   Retrieval     │
│    Agent        │     │    Agent        │
└────────┬────────┘     └────────┬────────┘
         │                      │
         │                      ▼
         │             ┌─────────────────┐
         │             │   Reasoning     │
         │             │    Agent        │
         │             └────────┬────────┘
         │                      │
         │                      ▼
         │             ┌─────────────────┐
         │             │  Generation     │
         │             │    Agent        │
         │             └────────┬────────┘
         │                      │
         │                      ▼
         │             ┌─────────────────┐
         │             │  Validation     │
         │             │    Agent        │
         │             └────────┬────────┘
         │                      │
         └──────────────────────┘
```

## 四、RAG实现方案

### 4.1 知识库架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     知识库构建流程                              │
│                                                                │
│  原始文档 ──→ 文本分块 ──→ 嵌入生成 ──→ 向量存储               │
│     │              │              │              │             │
│     ▼              ▼              ▼              ▼             │
│  Markdown      章节分割       BAAI/bge-m3    Chroma DB        │
│  PDF文档       知识点提取     向量维度:1024   HNSW索引         │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 检索流程

```
用户查询
    │
    ▼
┌─────────────────────────────────────┐
│ 步骤1: 多路召回 (Multi-path Recall) │
├─────────────────────────────────────┤
│ • 向量检索 (Chroma)                 │
│ • 关键词检索 (Full-text)            │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 步骤2: RRF融合 (Reciprocal Rank)   │
├─────────────────────────────────────┤
│ 公式: RRF(d) = Σ 1/(k + rank(d))  │
│ k=60, 融合多路召回结果              │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 步骤3: Rerank精排 (Reranking)      │
├─────────────────────────────────────┤
│ • BAAI/bge-reranker-v2-m3          │
│ • 过滤分数 < 0.3 的结果             │
└─────────────────────────────────────┘
    │
    ▼
最终检索结果 → LLM生成回答
```

### 4.3 检索策略

| 策略 | 说明 | 实现方式 |
|------|------|---------|
| 多路召回 | 同时进行向量检索和关键词检索 | Chroma向量检索 + BM25关键词检索 |
| RRF融合 | 对多路召回结果进行排名融合 | Reciprocal Rank Fusion |
| Rerank | 对检索结果进行相关性重排 | BAAI/bge-reranker-v2-m3 |
| 阈值过滤 | 设置相似度阈值 | 分数≥0.3 |
| Top-K | 返回前N个最相关结果 | K=5 |

## 五、SSE技术应用

### 5.1 流式输出架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     SSE数据流                                  │
│                                                                │
│  服务器 ──→ EventSource ──→ 前端                              │
│     │              │              │                            │
│     ▼              ▼              ▼                            │
│  推理阶段1      推理阶段2      推理阶段3                        │
│  路由决策       执行中         汇总结果                         │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 SSE事件类型

| 事件类型 | 说明 | 数据结构 |
|----------|------|---------|
| token | 回答片段 | {"content": "..."} |
| references | 引用来源 | {"source": "...", "score": 0.9} |
| error | 错误信息 | {"error": "..."} |

## 六、前端架构

### 6.1 组件结构

```
frontend/src/
├── components/
│   ├── course/          # 课程相关组件
│   │   └── CourseDetail.vue
│   ├── library/         # 电子书库组件
│   │   ├── BookDetail.vue
│   │   └── BookList.vue
│   ├── AgentWorkflow.vue
│   ├── AppHeader.vue
│   ├── ChatSection.vue
│   ├── CourseList.vue
│   ├── Dashboard.vue
│   ├── LearningRecords.vue
│   ├── LoginModal.vue
│   ├── MessageBubble.vue
│   ├── RegisterModal.vue
│   ├── Sidebar.vue
│   ├── SmartChat.vue
│   └── ...
├── stores/              # Pinia状态管理
│   ├── auth.js
│   ├── book.js
│   ├── chat.js
│   ├── course.js
│   ├── knowledge.js
│   └── learning.js
├── router/
│   └── index.js
├── App.vue
├── main.js
└── style.css
```

### 6.2 状态管理

| Store | 职责 | 核心状态 |
|-------|------|---------|
| auth | 用户认证状态 | isLoggedIn, currentUser, tokens |
| chat | 对话状态 | conversations, currentConversation, messages |
| course | 课程状态 | courses, selectedCourse, materials |
| book | 书籍状态 | books, categories, searchResults |
| learning | 学习状态 | records, recommendations |

## 七、技术栈详情

### 7.1 后端技术栈

| 分类 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 框架 | FastAPI | 0.115+ | 高性能异步API框架 |
| Agent | LangGraph | 1.x | 状态图编排 |
| 向量数据库 | Chroma | 0.5+ | 本地向量存储 |
| 业务数据库 | TiDB Cloud | MySQL兼容 | 云原生分布式数据库 |
| LLM | SiliconFlow API | - | OpenAI兼容接口 |
| JWT | python-jose | 3.3+ | 令牌认证 |
| 密码 | bcrypt | 4.0+ | 密码加密 |

### 7.2 前端技术栈

| 分类 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 框架 | Vue3 | 3.4+ | 响应式前端框架 |
| 状态管理 | Pinia | 2.1+ | 状态管理 |
| 样式 | Tailwind CSS | 3.4+ | 原子化CSS |
| HTTP | fetch | 内置 | HTTP客户端 |
| 图标 | Lucide Vue | 0.32+ | 图标库 |

## 八、部署架构

### 8.1 开发环境

```
前端开发服务器 (Vue + Vite)  http://localhost:5173
    ↓ HTTP请求
后端开发服务器 (FastAPI + Uvicorn)  http://localhost:8000
    ↓ 数据访问
TiDB Cloud (MySQL) + Chroma (本地)
```

### 8.2 生产环境

```
Nginx (反向代理)
    ↓
前端静态资源 (dist)
    ↓ API请求
FastAPI服务 (Uvicorn workers)
    ↓ 数据访问
TiDB Cloud + Chroma
```

## 九、环境变量配置

所有配置项通过 `backend/.env` 文件管理：

```env
# LLM配置
LLM_API_KEY=your-api-key
LLM_API_BASE=https://api.siliconflow.cn/v1
LLM_MODEL=Qwen/Qwen3-8B
LLM_MAX_TOKENS=1000
LLM_TEMPERATURE=0.7

# Embedding配置
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIMENSION=1024

# Rerank配置
RERANK_API_BASE=https://api.siliconflow.cn/v1
RERANK_MODEL=BAAI/bge-reranker-v2-m3
RERANK_TOP_N=3
RERANK_MIN_SCORE=0.3

# 数据库配置
DATABASE_URL=mysql+pymysql://...

# Chroma配置
CHROMA_DB_PATH=./cs_know_db
CHROMA_COLLECTION_NAME=cs_collection

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=false

# CORS配置
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## 十、安全架构

### 10.1 认证机制

- JWT令牌认证
- 访问令牌有效期24小时
- 密码使用bcrypt加密存储

### 10.2 数据安全

- 输入数据过滤和验证
- 防止SQL注入攻击
- 防止XSS攻击
- HTTPS传输加密

---

**文档版本**: v2.0  
**创建日期**: 2026年6月  
**适用项目**: 华南师范大学计算机专业课程管理系统
