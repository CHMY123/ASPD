"""
课程学习知识库问答系统 - FastAPI 应用入口

启动应用并进行依赖注入配置。
"""

import logging
import sys

# 配置日志 - 在所有其他导入之前设置
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 设置根日志器级别（根据DEBUG配置）
logging.basicConfig(
    level=logging.INFO,  # 默认INFO级别
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout)  # 输出到标准输出
    ],
    force=True  # 强制重新配置
)

# 设置关键模块的日志级别
logging.getLogger("agents").setLevel(logging.INFO)
logging.getLogger("agents.agents").setLevel(logging.INFO)
logging.getLogger("agents.base").setLevel(logging.INFO)
logging.getLogger("application").setLevel(logging.INFO)
logging.getLogger("infrastructure").setLevel(logging.INFO)
logging.getLogger("interfaces").setLevel(logging.INFO)

# 创建主日志器
logger = logging.getLogger(__name__)

# 打印日志配置确认
print("=" * 60)
print("日志系统已配置: INFO 级别")
print("=" * 60)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import (
    APP_HOST,
    APP_PORT,
    DEBUG,
    CORS_ORIGINS,
    KNOWLEDGE_BASE_PATH,
)
from infrastructure import (
    get_pool,
    init_database,
    close_database,
    LLMClient,
    ChromaKnowledgeRepository,
    PgConversationRepository,
    PgLearningRepository,
    PgUserRepository,
    AgentGraph,
)
from infrastructure.database_init import initialize_database, verify_database
from application import ChatService, KnowledgeService, LearningService, AuthService
from interfaces.api import chat_router, knowledge_router, learning_router, auth_router, upload_router, agent_router
from interfaces.api.chat_router import set_chat_service, set_coordination_agent as set_chat_coordination_agent
from interfaces.api.knowledge_router import set_knowledge_service
from interfaces.api.learning_router import set_learning_service
from interfaces.api.auth_router import set_auth_service
from interfaces.api.agent_router import set_coordination_agent


knowledge_service: KnowledgeService = None
learning_service: LearningService = None
chat_service: ChatService = None
auth_service: AuthService = None
agent_graph: AgentGraph = None
coordination_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    启动时初始化数据库连接池和服务实例，
    关闭时释放资源。
    """
    import logging
    logger = logging.getLogger(__name__)
    
    global knowledge_service, learning_service, chat_service, auth_service, agent_graph

    print("正在初始化数据库连接...")
    await init_database()

    print("正在初始化数据库表结构...")
    init_result = await initialize_database()
    if init_result["success"]:
        logger.info(f"数据库初始化成功: {init_result['tables_created']}")
        logger.info(f"索引创建: {init_result['indexes_created']}")
    else:
        logger.warning(f"数据库部分初始化失败: {init_result['errors']}")
    
    # 验证表结构
    tables_status = await verify_database()
    logger.info(f"表结构验证: {tables_status}")

    print("正在初始化 LLM 客户端...")
    llm_client = LLMClient()

    print("正在初始化仓储层...")
    knowledge_repo = ChromaKnowledgeRepository(llm_client)
    conversation_repo = PgConversationRepository()
    learning_repo = PgLearningRepository()
    user_repo = PgUserRepository()

    print("正在初始化认证服务...")
    auth_service = AuthService(user_repo)
    await auth_service.initialize()

    print("正在初始化知识库...")
    knowledge_service = KnowledgeService(knowledge_repo, llm_client)
    await knowledge_service.initialize()

    # 自动导入知识库（如果尚未导入）
    try:
        count = await knowledge_service.get_knowledge_count()
        if count == 0:
            print("知识库为空，正在自动导入...")
            import_result = await knowledge_service.import_from_folder(KNOWLEDGE_BASE_PATH)
            print(f"知识库导入完成: 共{import_result.total}个知识点，成功{import_result.imported}个，失败{import_result.failed}个")
        else:
            print(f"知识库已有 {count + 1} 个知识点，跳过导入")
    except Exception as e:
        print(f"知识库自动导入失败（可稍后手动调用 /init/knowledge 重试）: {e}")

    print("正在初始化学习服务...")
    learning_service = LearningService(learning_repo, knowledge_repo)
    await learning_service.initialize()

    print("正在初始化 Agent...")
    agent_graph = AgentGraph(knowledge_service, learning_service, llm_client)

    print("正在初始化多Agent协调器...")
    from agents import CoordinationAgent
    coordination_agent = CoordinationAgent(
        llm_client=llm_client,
        knowledge_repo=knowledge_repo
    )

    print("正在初始化问答服务...")
    chat_service = ChatService(agent_graph, conversation_repo)
    await chat_service.initialize()

    set_auth_service(auth_service)
    set_knowledge_service(knowledge_service)
    set_learning_service(learning_service)
    set_chat_service(chat_service)
    set_coordination_agent(coordination_agent)
    set_chat_coordination_agent(coordination_agent)

    print("初始化完成！")

    yield

    print("正在关闭数据库连接...")
    await close_database()
    print("应用已关闭")


app = FastAPI(
    title="课程学习知识库问答系统",
    description="""
## 项目介绍

这是一个基于课程知识库的智能问答系统，采用检索增强生成（RAG）架构，
通过向量数据库实现语义级别的知识匹配，结合大语言模型为学生提供精准、高效的知识检索与问答服务。

## 核心功能

- **智能问答**：基于知识库的智能问答，支持多轮对话
- **知识检索**：语义向量检索，快速定位相关知识点
- **学习跟踪**：记录学习行为，提供个性化推荐
- **知识收藏**：收藏重要知识点，方便复习

## 技术栈

- FastAPI + Uvicorn
- LangGraph Agent
- TiDB Cloud (MySQL兼容)
- Chroma Vector Database
- OpenAI API (Chat + Embedding)
    """,
    version="1.0.0",
    lifespan=lifespan,
    debug=DEBUG,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(knowledge_router)
app.include_router(learning_router)
app.include_router(upload_router)
app.include_router(agent_router)


@app.get("/", include_in_schema=False)
async def root():
    """根路径重定向到前端页面"""
    return {"message": "请访问前端页面 http://localhost:5173"}


@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "课程学习知识库问答系统",
        "version": "1.0.0"
    }


@app.get("/stats", tags=["系统"])
async def get_stats():
    """获取系统统计信息"""
    if knowledge_service is None:
        return {"error": "服务未初始化"}

    try:
        knowledge_count = await knowledge_service.get_knowledge_count()
        courses = await knowledge_service.get_all_courses()

        return {
            "knowledge_count": knowledge_count,
            "course_count": len(courses),
            "courses": courses
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/init/knowledge", tags=["系统"])
async def init_knowledge():
    """初始化知识库（从默认路径导入）"""
    if knowledge_service is None:
        return {"error": "服务未初始化"}

    try:
        result = await knowledge_service.import_from_folder(KNOWLEDGE_BASE_PATH)
        return {
            "success": True,
            "total": result.total,
            "imported": result.imported,
            "failed": result.failed
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    from uvicorn.config import LOGGING_CONFIG
    
    # 自定义 uvicorn 日志配置
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
    
    # 根据DEBUG配置设置日志级别
    log_level = "debug" if DEBUG else "info"
    
    # 根据DEBUG配置重新配置 agents 日志输出到 stderr
    for logger_name in ["agents", "agents.agents", "agents.base"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "%Y-%m-%d %H:%M:%S"
            ))
            logger.addHandler(handler)
    
    uvicorn.run(
        "main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=DEBUG,
        log_level=log_level,
    )
