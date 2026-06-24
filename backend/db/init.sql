-- 课程学习知识库问答系统 - 数据库初始化脚本
-- PostgreSQL + pgvector

-- 启用 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- 知识点向量表
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_embeddings (
    id              TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    content         TEXT NOT NULL,
    course          TEXT NOT NULL,
    chapter         TEXT,
    tags            TEXT[],
    source_file     TEXT NOT NULL,
    prerequisites   TEXT[],
    successors      TEXT[],
    related_ids     TEXT[],
    embedding       vector(1536) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建向量索引（加速相似度检索）
-- 使用 IVFFlat 索引，适合中等规模数据集
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding
ON knowledge_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 创建课程索引
CREATE INDEX IF NOT EXISTS idx_knowledge_course
ON knowledge_embeddings (course);

-- ============================================
-- 会话表
-- ============================================
CREATE TABLE IF NOT EXISTS conversations (
    id              TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL,
    title           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count   INTEGER DEFAULT 0
);

-- 创建用户会话索引
CREATE INDEX IF NOT EXISTS idx_conversations_user
ON conversations (user_id);

-- 创建更新时间索引
CREATE INDEX IF NOT EXISTS idx_conversations_updated
ON conversations (updated_at DESC);

-- ============================================
-- 消息表
-- ============================================
CREATE TABLE IF NOT EXISTS messages (
    id              TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role            TEXT NOT NULL,
    content         TEXT NOT NULL,
    references      TEXT[],
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE
);

-- 创建会话消息索引
CREATE INDEX IF NOT EXISTS idx_messages_conversation
ON messages (conversation_id);

-- 创建消息时间索引
CREATE INDEX IF NOT EXISTS idx_messages_created
ON messages (created_at);

-- ============================================
-- 学习记录表
-- ============================================
CREATE TABLE IF NOT EXISTS learning_records (
    id                  TEXT PRIMARY KEY,
    user_id             TEXT NOT NULL,
    knowledge_point_id  TEXT NOT NULL,
    action              TEXT NOT NULL,
    duration            INTEGER DEFAULT 0,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建用户学习记录索引
CREATE INDEX IF NOT EXISTS idx_learning_user
ON learning_records (user_id, created_at DESC);

-- 创建知识点学习记录索引
CREATE INDEX IF NOT EXISTS idx_learning_knowledge
ON learning_records (knowledge_point_id);

-- ============================================
-- 知识收藏表
-- ============================================
CREATE TABLE IF NOT EXISTS knowledge_collections (
    id                  TEXT PRIMARY KEY,
    user_id             TEXT NOT NULL,
    knowledge_point_id  TEXT NOT NULL,
    folder              TEXT DEFAULT '默认收藏夹',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note                TEXT DEFAULT '',
    CONSTRAINT uq_user_knowledge
        UNIQUE (user_id, knowledge_point_id)
);

-- 创建用户收藏索引
CREATE INDEX IF NOT EXISTS idx_collections_user
ON knowledge_collections (user_id);

-- 创建收藏夹索引
CREATE INDEX IF NOT EXISTS idx_collections_folder
ON knowledge_collections (user_id, folder);

-- ============================================
-- 用户表（可选，用于完整用户系统）
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id              TEXT PRIMARY KEY,
    username        TEXT UNIQUE NOT NULL,
    email           TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    role            TEXT DEFAULT 'student',
    status          TEXT DEFAULT 'active',
    avatar          TEXT DEFAULT '',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 课程表
-- ============================================
CREATE TABLE IF NOT EXISTS courses (
    id              TEXT PRIMARY KEY,
    course_code     TEXT UNIQUE NOT NULL,
    course_name     TEXT NOT NULL,
    credits         DECIMAL(3,1) NOT NULL,
    hours           INTEGER NOT NULL,
    semester        TEXT NOT NULL,
    course_type     TEXT DEFAULT 'required',
    teacher_name    TEXT NOT NULL,
    teacher_title   TEXT DEFAULT '',
    schedule        TEXT DEFAULT '',
    location        TEXT DEFAULT '',
    class_location  VARCHAR(500) DEFAULT '',
    class_time      VARCHAR(500) DEFAULT '',
    cover           TEXT DEFAULT '',
    description     TEXT DEFAULT '',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建课程代码索引
CREATE INDEX IF NOT EXISTS idx_courses_code
ON courses (course_code);

-- 创建学期索引
CREATE INDEX IF NOT EXISTS idx_courses_semester
ON courses (semester);

-- ============================================
-- 电子书表
-- ============================================
CREATE TABLE IF NOT EXISTS ebooks (
    id                  TEXT PRIMARY KEY,
    title               TEXT NOT NULL,
    subtitle            TEXT DEFAULT '',
    author              TEXT NOT NULL,
    translator          TEXT DEFAULT '',
    publisher           TEXT NOT NULL,
    publish_date        TEXT DEFAULT '',
    isbn                TEXT UNIQUE,
    category            TEXT DEFAULT '',
    summary             TEXT DEFAULT '',
    table_of_contents   TEXT DEFAULT '',
    cover               TEXT DEFAULT '',
    file_url            TEXT DEFAULT '',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建书名索引
CREATE INDEX IF NOT EXISTS idx_ebooks_title
ON ebooks (title);

-- 创建分类索引
CREATE INDEX IF NOT EXISTS idx_ebooks_category
ON ebooks (category);

-- 创建ISBN索引
CREATE INDEX IF NOT EXISTS idx_ebooks_isbn
ON ebooks (isbn);

-- 创建用户名索引
CREATE INDEX IF NOT EXISTS idx_users_username
ON users (username);

-- 创建邮箱索引
CREATE INDEX IF NOT EXISTS idx_users_email
ON users (email);

-- ============================================
-- 注释说明
-- ============================================
COMMENT ON TABLE knowledge_embeddings IS '课程知识库向量表';
COMMENT ON TABLE conversations IS '问答会话表';
COMMENT ON TABLE messages IS '会话消息表';
COMMENT ON TABLE learning_records IS '学习记录表';
COMMENT ON TABLE knowledge_collections IS '知识收藏表';
COMMENT ON TABLE users IS '用户表';

COMMENT ON COLUMN knowledge_embeddings.embedding IS '1024维向量（BAAI/bge-m3模型）';
COMMENT ON COLUMN learning_records.action IS '操作类型：view/search/collect/ask/browse/review';
