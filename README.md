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
- 流式输出，打字机效果
- 检索结果引用来源清晰可追溯
- 支持知识点关联推荐

### 多智能体协同对话
- **课程咨询Agent**：课程信息查询、教学进度咨询
- **代码解答Agent**：代码问题解答、算法实现指导
- **电子书资讯Agent**：书籍推荐、内容检索
- **知识讲解Agent**：概念解释、原理阐述
- **学习规划Agent**：学习路径建议、复习计划制定

### LLM模式设置
- **知识检索模式**：专注于专业知识查询，严格基于知识库
- **对话模式**：日常学习交流，开放域对话

## 技术栈

| 层次 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue3 | 3.4+ |
| 状态管理 | Pinia | 2.1+ |
| 样式框架 | Tailwind CSS | 3.4+ |
| 后端框架 | FastAPI | 0.115+ |
| Agent框架 | LangGraph | 1.x |
| 向量数据库 | Chroma | 0.5+ |
| 业务数据库 | TiDB Cloud | MySQL兼容 |
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
│   └── multi_agent_system_architecture.md  # 多Agent架构文档
│
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
# 或使用uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

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

# Embedding配置
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIMENSION=1024

# Rerank配置
RERANK_API_BASE=https://api.siliconflow.cn/v1
RERANK_MODEL=BAAI/bge-reranker-v2-m3

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

## 文档清单

| 文档 | 说明 |
|------|------|
| requirement.md | 需求文档 |
| database_design.md | 数据库设计文档 |
| technical_architecture.md | 技术架构文档 |
| STARTUP_GUIDE.md | 启动指南 |
| docs/RAG_TECHNICAL_DOCUMENTATION.md | RAG技术文档 |
| docs/multi_agent_system_architecture.md | 多Agent架构文档 |

## 许可证

MIT License
