# 课程学习知识库问答系统 - 启动指南

## 环境要求

### 硬件要求
- CPU：双核及以上
- 内存：4GB及以上
- 存储空间：至少2GB可用空间

### 软件要求
| 软件 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | 后端开发语言 |
| Node.js | 20+ | 前端开发环境 |
| npm | 9+ | Node.js包管理器 |

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd gjrjsx
```

### 2. 安装后端依赖

```bash
cd backend
python -m venv venv

# Windows激活虚拟环境
venv\Scripts\activate

# Linux/Mac激活虚拟环境
source venv/bin/activate

pip install -r requirements.txt
```

> **注意**：如果遇到安装失败，可能需要安装系统依赖：
> - Ubuntu/Debian：`sudo apt-get install python3-dev libmysqlclient-dev`
> - CentOS/RHEL：`sudo yum install python3-devel mysql-community-devel`

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 配置环境变量

在 `backend/` 目录下创建 `.env` 文件，参考 `.env.example`：

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
RERANK_TOP_N=3
RERANK_MIN_SCORE=0.3

# 数据库配置
DATABASE_URL=mysql+pymysql://user:password@host:port/database

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

## 启动服务

### 开发模式

#### 步骤1：启动后端服务

```bash
cd backend
python main.py
```

**Windows环境注意事项**：
- Windows平台会自动使用SelectorEventLoopPolicy，确保aiomysql SSL连接兼容性
- 若遇到编码问题，确保已设置环境变量：`set PYTHONIOENCODING=utf-8`
- 请勿使用`uvicorn main:app --reload`命令，后端已在main.py中处理了Windows事件循环问题

#### 步骤2：启动前端开发服务器

```bash
cd frontend
npm run dev
```

### 生产模式

#### 步骤1：构建前端

```bash
cd frontend
npm run build
```

#### 步骤2：启动后端服务

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost:5173 | Vue开发服务器 |
| 后端API | http://localhost:8000 | FastAPI服务 |
| API文档 | http://localhost:8000/docs | Swagger UI |
| API文档 | http://localhost:8000/redoc | ReDoc |

## 使用说明

### 1. 注册账户

1. 访问 http://localhost:5173
2. 点击右上角「注册」按钮
3. 填写用户名、邮箱、密码
4. 点击「注册」完成账户创建

### 2. 登录系统

1. 点击右上角「登录」按钮
2. 输入用户名和密码
3. 点击「登录」进入系统

### 3. 开始问答

1. 在输入框中输入问题
2. 按Enter键或点击「发送」按钮
3. 等待系统返回回答
4. 查看相关知识点推荐

## 常见问题

### 问题1：无法从源解析导入"jose.jwt"

**原因**：缺少`python-jose`依赖

**解决方案**：
```bash
cd backend
pip install python-jose[cryptography]==3.3.0
```

### 问题2：无法连接到TiDB Cloud数据库

**解决方案**：
1. 检查网络连接
2. 验证`.env`中的数据库连接字符串是否正确
3. 检查TiDB Cloud控制台的IP白名单设置

### 问题3：Chroma数据库初始化失败

**解决方案**：
1. 检查`backend/cs_know_db`目录是否有读写权限
2. 确保chromadb依赖已正确安装
3. 尝试删除`cs_know_db`目录后重新启动

### 问题4：前端页面空白

**解决方案**：
1. 检查浏览器控制台是否有错误信息
2. 验证后端API服务是否正常运行
3. 检查前端构建是否成功

### 问题5：LLM API调用失败

**解决方案**：
1. 检查API密钥是否正确配置
2. 验证网络连接可以访问API服务器
3. 检查API调用频率是否超限

### 问题6：Windows环境下数据库连接失败（SSLWantReadError/OSError: [WinError 87]）

**原因**：Windows默认使用ProactorEventLoop，与aiomysql的SSL连接存在IOCP兼容性问题

**解决方案**：
1. 使用`python main.py`命令启动，后端已自动设置WindowsSelectorEventLoopPolicy
2. 确保Python版本为3.11+

### 问题7：'gbk' codec can't encode character错误

**原因**：Windows默认使用GBK编码，无法编码Unicode字符

**解决方案**：
1. 设置环境变量：`set PYTHONIOENCODING=utf-8`
2. 后端已在代码中添加UTF-8编码支持

### 问题8：uvicorn启动报错（Error loading custom loop setup function）

**原因**：uvicorn的loop参数不支持某些值

**解决方案**：
1. 使用`python main.py`命令启动，后端已处理此问题

## 项目结构

```
gjrjsx/
├── frontend/           # 前端项目
│   ├── src/            # Vue3源代码
│   │   ├── components/ # Vue组件
│   │   ├── stores/     # Pinia状态管理
│   │   └── ...
│   └── ...
│
├── backend/            # 后端项目
│   ├── main.py         # FastAPI入口
│   ├── config.py       # 配置文件
│   ├── requirements.txt # Python依赖
│   ├── agents/         # Agent模块
│   ├── application/    # 应用服务
│   ├── infrastructure/ # 基础设施
│   ├── interfaces/     # API路由
│   ├── domain/         # 领域模型
│   ├── common/         # 公共模块
│   ├── tests/          # 单元测试
│   ├── db/             # 数据库脚本
│   └── cs_know_db/     # Chroma向量数据库
│
├── docs/               # 文档目录
│   └── knowledge/      # Markdown知识文件
│
├── .env.example        # 环境变量模板
└── ...
```

## 运行测试

```bash
cd backend
pytest tests/
```

## 注意事项

1. **首次启动**：系统会自动初始化Chroma向量数据库，可能需要一些时间
2. **API密钥**：确保已正确配置SiliconFlow API密钥
3. **数据库连接**：首次连接TiDB Cloud可能需要等待白名单生效
4. **学习推荐**：登录后才能获取个性化学习推荐

---

**文档版本**：v3.0  
**更新时间**：2026年6月  
**适用项目**：课程学习知识库问答系统
