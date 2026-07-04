# 华南师范大学计算机专业课程管理系统

基于检索增强生成（RAG）架构和多智能体协同机制的智能课程管理系统，为华南师范大学计算机专业学生提供课程信息管理、电子资源访问、智能知识检索及多智能体协同对话等功能。

## 功能特性

### 课程管理
- 已选课程列表展示（课程名称、教师信息、学分、上课时间）
- 课程详情页（课程大纲、教学进度、考核方式）
- 课程资料查看与下载（课件、讲义、补充材料）
- 课程搜索功能（按课程名称、教师姓名检索）

### 电子书库
- 按课程关联检索推荐书籍
- 按专业分类检索（数据结构、算法、操作系统等）
- 关键词检索（书名、作者、ISBN）
- 书籍信息展示（封面、简介、目录）

### 智能知识检索
- 基于RAG架构的专业知识问答
- 多路召回策略（向量检索 + 关键词检索）
- RRF（Reciprocal Rank Fusion）结果融合算法
- Rerank精排机制，提升检索精度
- 流式输出，打字机效果
- 检索结果引用来源清晰可追溯
- 支持知识点关联推荐

### 多智能体协同对话
- **理解Agent**：意图识别、实体提取、问题分类
- **检索Agent**：向量知识库检索、数据库查询双路径
- **推理Agent**：逻辑推理、上下文分析
- **生成Agent**：答案生成、智能提示词切换
- **验证Agent**：答案准确性验证、质量评分
- **推荐Agent**：相关知识推荐、学习路径建议
- 工作流实时状态展示，可视化执行过程

### LLM模式设置
- **知识检索模式**：专注于专业知识查询，严格基于知识库
- **对话模式**：日常学习交流，开放域对话

## 架构亮点

### RAG检索增强生成
- **多路召回策略**：向量检索（语义相似度）+ 关键词检索（全文匹配）双路径召回
- **RRF融合算法**：使用倒数排名融合（Reciprocal Rank Fusion）合并多路召回结果，无需调参，鲁棒性强
- **Rerank精排**：使用BAAI/bge-reranker-v2-m3模型对融合结果进行精排，提升检索精度
- **BGE-M3向量模型**：1024维向量表示，支持非对称检索（`query:`/`passage:`前缀）

### 多Agent协同对话
- **六Agent架构**：理解→检索→推理→生成→验证→推荐，形成完整的知识问答流程
- **意图驱动路由**：根据用户意图自动选择向量知识库或关系数据库作为数据来源
- **实时工作流展示**：通过SSE（Server-Sent Events）技术实时推送各Agent执行状态，可视化工作流进度
- **多层次质量验证**：综合内容检查得分（60%）和LLM验证得分（40%），保障答案质量

## 技术栈

| 层次 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue3 | 3.4.21 |
| 状态管理 | Pinia | 2.1.7 |
| 样式框架 | Tailwind CSS | 3.4.1 |
| 构建工具 | Vite | 5.1.6 |
| 后端框架 | FastAPI | 0.123.5 |
| ASGI服务器 | Uvicorn | 0.34.0 |
| Agent框架 | LangGraph | 1.0.5 |
| LLM集成 | langchain-openai | 1.2.2 |
| 向量数据库 | Chroma | 1.4.0 |
| 业务数据库 | TiDB Cloud | MySQL兼容 |
| ORM | aiomysql / pymysql | 0.3.2 / 1.1.1 |
| 数据验证 | Pydantic | 2.12.5 |
| 文件存储 | boto3 (缤纷云) | 1.42.9 |
| LLM接口 | SiliconFlow (OpenAI兼容) | - |

## 项目结构

```
gjrjsx/
├── frontend/                    # 前端项目
│   ├── src/                     # Vue3源代码
│   │   ├── components/          # Vue组件
│   │   │   ├── course/          # 课程相关组件
│   │   │   ├── library/         # 电子书库组件
│   │   │   └── *.vue            # 通用组件
│   │   ├── stores/              # Pinia状态管理
│   │   ├── router/              # 路由配置
│   │   ├── App.vue              # 根组件
│   │   ├── main.js              # 入口文件
│   │   └── style.css            # 全局样式
│   ├── index.html               # HTML入口
│   ├── package.json             # Node依赖配置
│   ├── vite.config.js           # Vite配置
│   ├── tailwind.config.js       # Tailwind配置
│   └── postcss.config.js        # PostCSS配置
│
├── backend/                     # 后端项目
│   ├── main.py                  # FastAPI入口
│   ├── config.py                # 配置文件（从.env读取）
│   ├── requirements.txt         # Python依赖
│   ├── demo.py                   # RAG示例代码
│   ├── .env                      # 环境变量配置
│   │
│   ├── agents/                   # Agent模块
│   │   ├── agents.py             # Agent实现（Understanding/Retrieval/Generation等）
│   │   └── base.py               # Agent基类
│   │
│   ├── application/             # 应用层
│   │   ├── auth_service.py       # 认证服务
│   │   ├── chat_service.py       # 问答服务
│   │   ├── knowledge_service.py  # 知识库服务
│   │   └── learning_service.py   # 学习服务
│   │
│   ├── infrastructure/           # 基础设施层
│   │   ├── database.py           # 数据库连接池
│   │   ├── database_init.py      # 数据库初始化
│   │   ├── llm_client.py         # LLM/Embedding/Rerank封装
│   │   ├── knowledge_repository.py  # Chroma向量库实现
│   │   ├── conversation_repository.py  # 会话仓储
│   │   ├── learning_repository.py # 学习记录仓储
│   │   ├── user_repository.py    # 用户仓储
│   │   ├── storage_service.py    # 文件存储服务
│   │   └── agent/                 # LangGraph Agent
│   │       ├── graph.py          # Agent编排图
│   │       └── tools.py          # Agent工具
│   │
│   ├── interfaces/              # 接口层
│   │   ├── api/                  # API路由
│   │   │   ├── auth_router.py    # 认证接口
│   │   │   ├── chat_router.py    # 问答接口
│   │   │   ├── knowledge_router.py  # 知识库接口
│   │   │   ├── learning_router.py  # 学习接口
│   │   │   ├── upload_router.py   # 上传接口
│   │   │   └── agent_router.py   # Agent接口
│   │   └── schemas/              # Pydantic模型
│   │       ├── chat_schema.py
│   │       ├── knowledge_schema.py
│   │       └── learning_schema.py
│   │
│   ├── domain/                  # 领域层
│   │   ├── user/                # 用户领域
│   │   ├── knowledge/           # 知识领域
│   │   ├── conversation/        # 对话领域
│   │   └── learning/            # 学习领域
│   │
│   ├── common/                  # 公共模块
│   │   ├── exceptions.py        # 异常定义
│   │   ├── logger.py             # 日志配置
│   │   └── validators.py         # 验证器
│   │
│   ├── tests/                   # 单元测试
│   │   ├── test_auth_service.py
│   │   ├── test_knowledge_service.py
│   │   ├── test_llm_client.py
│   │   └── test_validators.py
│   │
│   ├── db/                      # 数据库脚本
│   │   └── init.sql             # 初始化SQL
│   │
│   └── cs_know_db/              # Chroma向量数据库
│
├── docs/                        # 文档目录
│   ├── knowledge/               # Markdown知识文件
│   ├── RAG_TECHNICAL_DOCUMENTATION.md  # RAG技术文档
│   ├── multi_agent_system_architecture.md  # 多Agent架构文档
│   └── presentation_script.md   # 项目视频讲解演讲稿
│
├── .gitignore                   # Git忽略规则
├── requirement.md               # 需求文档
├── database_design.md           # 数据库设计文档
├── technical_architecture.md    # 技术架构文档
├── STARTUP_GUIDE.md             # 启动指南
├── PRODUCT.md                   # 产品文档
├── DESIGN.md                    # 设计规范
└── README.md                    # 项目说明文档
```

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+
- npm 9+

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd gjrjsx
```

2. **安装后端依赖**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

3. **安装前端依赖**
```bash
cd frontend
npm install
```

4. **配置环境变量**
```bash
cd backend
# 编辑.env文件，配置API密钥和其他配置
```

5. **启动后端服务**
```bash
cd backend
python main.py
```

> **注意**: 在Windows环境下，`python main.py`会自动配置`WindowsSelectorEventLoopPolicy`，避免与aiomysql的SSL连接兼容性问题。请不要使用`uvicorn main:app --reload`命令启动。

6. **启动前端开发服务器**
```bash
cd frontend
npm run dev
```

7. **访问应用**
- 前端界面：http://localhost:5173
- API文档：http://localhost:8000/docs

## 数据库配置

### TiDB Cloud
```
连接字符串: mysql+pymysql://<user>:<password>@<host>:<port>/<database>
```

### Chroma
```
存储路径: backend/cs_know_db
集合名称: cs_collection
```

## 环境变量配置

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
EMBEDDING_API_BASE=https://api.siliconflow.cn/v1

# Rerank配置
RERANK_API_BASE=https://api.siliconflow.cn/v1
RERANK_MODEL=BAAI/bge-reranker-v2-m3
RERANK_MAX_LENGTH=512
RERANK_TOP_N=5
RERANK_MIN_SCORE=0.3

# RRF (Reciprocal Rank Fusion) 配置
RRF_K=60

# 相似度阈值
SIMILARITY_THRESHOLD=0.5

# 数据库配置
DATABASE_URL=mysql+pymysql://...

# Chroma配置
CHROMA_DB_PATH=./cs_know_db
CHROMA_COLLECTION_NAME=cs_collection

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=false
KNOWLEDGE_BASE_PATH=../docs/knowledge
MAX_SEARCH_RESULTS=5

# CORS配置
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# 缤纷云存储配置
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
S3_ENDPOINT_URL=https://s3.bitiful.net
S3_BUCKET_NAME=your-bucket-name

# 文件上传配置
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,webp
```

## API接口

### 认证接口
- POST /api/auth/register - 用户注册
- POST /api/auth/login - 用户登录
- POST /api/auth/refresh - 刷新令牌
- GET /api/auth/me - 获取用户信息

### 课程接口
- GET /api/knowledge/courses - 获取课程列表
- GET /api/knowledge/courses/{id} - 获取课程详情
- POST /api/knowledge/courses - 添加课程

### 电子书接口
- GET /api/knowledge/books - 获取书籍列表
- GET /api/knowledge/books/{id} - 获取书籍详情
- POST /api/knowledge/books - 添加书籍

### 问答接口
- POST /api/chat/knowledge/stream - 知识检索模式（流式）
- POST /api/chat/message - 对话模式
- GET /api/chat/{thread_id}/history - 获取会话历史

### 多Agent接口
- POST /api/agents/query/stream - 多Agent协同查询（流式，实时推送工作流状态）
- POST /api/agents/query - 多Agent协同查询（同步）

## 文档清单

| 文档 | 说明 |
|------|------|
| requirement.md | 需求文档 |
| database_design.md | 数据库设计文档 |
| technical_architecture.md | 技术架构文档 |
| STARTUP_GUIDE.md | 启动指南 |
| docs/RAG_TECHNICAL_DOCUMENTATION.md | RAG技术文档 |
| docs/multi_agent_system_architecture.md | 多Agent架构文档 |
| docs/presentation_script.md | 项目视频讲解演讲稿 |

## 许可证

MIT License
