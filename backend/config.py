"""
配置文件

管理应用程序的配置项。
所有配置项均从.env文件读取。
"""

import os
from dotenv import load_dotenv

load_dotenv()

# LLM配置
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
LLM_API_BASE: str = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1000"))
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# Embedding配置
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "1024"))
EMBEDDING_API_BASE: str = os.getenv("EMBEDDING_API_BASE", "https://api.siliconflow.cn/v1")

# Rerank配置
RERANK_API_BASE: str = os.getenv("RERANK_API_BASE", "https://api.siliconflow.cn/v1")
RERANK_MODEL: str = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")
RERANK_MAX_LENGTH: int = int(os.getenv("RERANK_MAX_LENGTH", "512"))
RERANK_TOP_N: int = int(os.getenv("RERANK_TOP_N", "5"))
RERANK_MIN_SCORE: float = float(os.getenv("RERANK_MIN_SCORE", "0.3"))

# RRF (Reciprocal Rank Fusion) 配置
RRF_K: int = int(os.getenv("RRF_K", "60"))

# 相似度阈值
SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))

# TiDB Cloud 数据库连接配置
DATABASE_URL: str = os.getenv("DATABASE_URL", "")

# 本地Chroma向量数据库配置
CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./cs_know_db")
CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "cs_collection")

# 应用配置
APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

KNOWLEDGE_BASE_PATH: str = os.getenv("KNOWLEDGE_BASE_PATH", "../docs/knowledge")
MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))

# CORS配置
CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
CORS_ALLOW_METHODS: list = os.getenv("CORS_ALLOW_METHODS", "*").split(",") if os.getenv("CORS_ALLOW_METHODS", "*") != "*" else ["*"]
CORS_ALLOW_HEADERS: list = os.getenv("CORS_ALLOW_HEADERS", "*").split(",") if os.getenv("CORS_ALLOW_HEADERS", "*") != "*" else ["*"]

# 缤纷云存储配置
S3_ACCESS_KEY_ID: str = os.getenv("S3_ACCESS_KEY_ID", "")
S3_SECRET_ACCESS_KEY: str = os.getenv("S3_SECRET_ACCESS_KEY", "")
S3_ENDPOINT_URL: str = os.getenv("S3_ENDPOINT_URL", "https://s3.bitiful.net")
S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "aspd")

# 文件上传配置
MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
ALLOWED_EXTENSIONS: list = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif,webp").split(",")
