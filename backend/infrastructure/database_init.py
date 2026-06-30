"""
数据库初始化管理 (Database Initialization Manager)

严格按照数据库设计文档实现，支持表结构创建、索引创建、事务处理和日志记录。
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from infrastructure.database import get_pool, fetch_sql, fetchrow_sql, execute_sql

logger = logging.getLogger(__name__)


class InitOrder(Enum):
    """初始化顺序枚举"""
    USERS = 1
    COURSES = 2
    ENROLLMENTS = 3
    BOOKS = 4
    CONVERSATIONS = 5
    MESSAGES = 6
    MESSAGE_REFERENCES = 7
    LEARNING_RECORDS = 8
    KNOWLEDGE_COLLECTIONS = 9


@dataclass
class TableSchema:
    """表结构定义"""
    name: str
    create_sql: str
    indexes: List[Dict[str, str]]
    seed_data: Optional[List[tuple]] = None


class DatabaseInitializer:
    """
    数据库初始化器

    严格按照数据库设计文档实现表结构初始化。
    """

    def __init__(self):
        self._initialized_tables: set = set()
        self._errors: List[Dict[str, Any]] = []

    async def initialize_all(self) -> Dict[str, Any]:
        """
        初始化所有数据库表

        Returns:
            Dict: 初始化结果
        """
        result = {
            "success": True,
            "tables_created": [],
            "tables_already_exist": [],
            "indexes_created": [],
            "errors": []
        }

        try:
            version = await fetchrow_sql("SELECT VERSION() as version")
            logger.info(f"数据库版本: {version['version']}")

            schemas = self._get_all_schemas()
            for order in sorted(schemas.keys(), key=lambda x: x.value):
                table_name = schemas[order]["name"]
                try:
                    created = await self._create_table(schemas[order])
                    if created:
                        result["tables_created"].append(table_name)
                        logger.info(f"表 {table_name} 创建成功")
                    else:
                        result["tables_already_exist"].append(table_name)
                        logger.info(f"表 {table_name} 已存在")
                except Exception as e:
                    error_msg = f"表 {table_name} 创建失败: {str(e)}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)
                    result["success"] = False

            # 执行数据库迁移（为已有表添加缺失的列）
            await self._run_migrations()

            for order in sorted(schemas.keys(), key=lambda x: x.value):
                table_schema = schemas[order]
                for idx in table_schema.get("indexes", []):
                    try:
                        created = await self._create_index(idx)
                        if created:
                            result["indexes_created"].append(idx["name"])
                            logger.info(f"索引 {idx['name']} 创建成功")
                        else:
                            logger.info(f"索引 {idx['name']} 已存在")
                    except Exception as e:
                        logger.warning(f"索引 {idx['name']} 创建失败: {str(e)}")

            for order in sorted(schemas.keys(), key=lambda x: x.value):
                table_schema = schemas[order]
                if table_schema.get("seed_data"):
                    for data in table_schema["seed_data"]:
                        try:
                            await self._insert_seed_data(table_schema["name"], data)
                            logger.info(f"初始数据插入成功: {table_schema['name']}")
                        except Exception as e:
                            logger.warning(f"初始数据插入失败: {str(e)}")

        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            result["success"] = False
            result["errors"].append(str(e))

        return result

    async def _create_table(self, schema: Dict[str, Any]) -> bool:
        """
        创建表

        Args:
            schema: 表结构定义

        Returns:
            bool: 是否创建新表
        """
        table_name = schema["name"]
        
        row = await fetchrow_sql(
            "SELECT COUNT(*) as count FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = %s",
            (table_name,)
        )
        
        if row and row["count"] == 0:
            await execute_sql(schema["create_sql"])
            return True
        return False

    async def _create_index(self, index_def: Dict[str, str]) -> bool:
        """
        创建索引（如果不存在）

        Args:
            index_def: 索引定义

        Returns:
            bool: 是否创建新索引
        """
        index_name = index_def["name"]
        table_name = index_def.get("table") or index_name.split("_")[1] if "_" in index_name else None
        
        if table_name:
            row = await fetchrow_sql(
                "SELECT COUNT(*) as count FROM information_schema.statistics "
                "WHERE table_schema = DATABASE() AND table_name = %s AND index_name = %s",
                table_name, 
                index_name
            )
            
            if row and row["count"] > 0:
                logger.info(f"索引 {index_name} 已存在，跳过创建")
                return False
        
        try:
            await execute_sql(index_def["sql"])
            return True
        except Exception as e:
            logger.warning(f"索引 {index_name} 创建失败: {str(e)}")
            return False
                
    async def _insert_seed_data(self, table_name: str, data: tuple) -> None:
        """
        插入初始数据

        Args:
            table_name: 表名
            data: 数据元组
        """
        columns = await self._get_table_columns(table_name)
        if len(columns) == len(data):
            placeholders = ",".join(["%s"] * len(data))
            sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
            await execute_sql(sql, *data)

    async def _run_migrations(self) -> None:
        """
        执行数据库迁移

        为已有表添加新版本中新增的列，无需删除重建。
        """
        migrations = [
            # 迁移1: 为messages表添加workflow_details列（支持多Agent工作流）
            (
                "messages",
                "workflow_details",
                "ALTER TABLE messages ADD COLUMN workflow_details JSON AFTER `references`"
            ),
        ]

        for table_name, column_name, alter_sql in migrations:
            try:
                # 检查列是否已存在
                row = await fetchrow_sql(
                    "SELECT COUNT(*) as count FROM information_schema.columns "
                    "WHERE table_schema = DATABASE() AND table_name = %s AND column_name = %s",
                    table_name, column_name
                )
                if row and row["count"] == 0:
                    await execute_sql(alter_sql)
                    logger.info(f"迁移成功: 表 {table_name} 添加列 {column_name}")
                else:
                    logger.debug(f"迁移跳过: 列 {column_name} 已存在于表 {table_name}")
            except Exception as e:
                logger.warning(f"迁移失败: 表 {table_name} 添加列 {column_name}: {e}")

        # 创建默认管理员账号（如果不存在）
        await self._ensure_admin_user()

    async def _ensure_admin_user(self) -> None:
        """
        确保存在默认管理员账号
        """
        try:
            # 检查是否已存在管理员
            admin_exists = await fetchrow_sql(
                "SELECT COUNT(*) as count FROM users WHERE role = 'admin'"
            )
            if admin_exists and admin_exists["count"] > 0:
                logger.debug("管理员账号已存在，跳过创建")
                return

            # 生成密码哈希（使用bcrypt）
            import bcrypt
            password = "admin123"
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

            # 创建管理员账号
            import uuid
            from datetime import datetime
            admin_id = str(uuid.uuid4())
            now = datetime.now().isoformat()

            await execute_sql(
                """
                INSERT INTO users (id, username, email, password_hash, real_name, role, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                admin_id,
                "admin",
                "admin@system.local",
                password_hash,
                "系统管理员",
                "admin",
                True,
                now,
                now
            )
            logger.info("默认管理员账号创建成功: admin / admin123")
        except Exception as e:
            logger.warning(f"创建默认管理员失败: {e}")

    async def _get_table_columns(self, table_name: str) -> List[str]:
        """
        获取表列名

        Args:
            table_name: 表名

        Returns:
            List[str]: 列名列表
        """
        results = await fetch_sql(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = %s "
            "ORDER BY ordinal_position",
            (table_name,)
        )
        return [r["column_name"] for r in results]

    def _get_all_schemas(self) -> Dict[InitOrder, Dict[str, Any]]:
        """
        获取所有表结构定义（严格按照数据库设计文档）

        Returns:
            Dict: 表结构映射
        """
        return {
            InitOrder.USERS: {
                "name": "users",
                "create_sql": """
                    CREATE TABLE IF NOT EXISTS users (
                        id              VARCHAR(36) PRIMARY KEY,
                        student_id      VARCHAR(20) UNIQUE,
                        username        VARCHAR(100) NOT NULL,
                        email           VARCHAR(255) UNIQUE,
                        password_hash   VARCHAR(255) NOT NULL,
                        real_name       VARCHAR(50) NOT NULL,
                        major           VARCHAR(100),
                        grade           VARCHAR(20),
                        role            VARCHAR(20) DEFAULT 'student',
                        is_active       BOOLEAN DEFAULT true,
                        avatar          VARCHAR(500) DEFAULT '',
                        last_login      DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status          VARCHAR(20) DEFAULT 'active',
                        created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """,
                "indexes": [
                    {"name": "idx_users_username", "table": "users", "sql": "CREATE INDEX idx_users_username ON users (username)"},
                    {"name": "idx_users_email", "table": "users", "sql": "CREATE INDEX idx_users_email ON users (email)"},
                    {"name": "idx_users_student_id", "table": "users", "sql": "CREATE INDEX idx_users_student_id ON users (student_id)"}
                ]
            },
            InitOrder.COURSES: {
                "name": "courses",
                "create_sql": """
                    CREATE TABLE IF NOT EXISTS courses (
                        id              VARCHAR(36) PRIMARY KEY,
                        course_code     VARCHAR(50) UNIQUE,
                        course_name     VARCHAR(200) NOT NULL,
                        credits         DECIMAL(3,1) NOT NULL,
                        hours           INT NOT NULL,
                        semester        VARCHAR(20) NOT NULL,
                        course_type     VARCHAR(20) DEFAULT 'required',
                        description     TEXT,
                        teacher_name    VARCHAR(100) NOT NULL,
                        teacher_title   VARCHAR(50) DEFAULT '',
                        schedule        VARCHAR(500) DEFAULT '',
                        location        VARCHAR(500) DEFAULT '',
                        class_location  VARCHAR(500) DEFAULT '',
                        class_time      VARCHAR(500) DEFAULT '',
                        cover           VARCHAR(500) DEFAULT '',
                        created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """,
                "indexes": [
                    {"name": "idx_courses_code", "table": "courses", "sql": "CREATE INDEX idx_courses_code ON courses (course_code)"},
                    {"name": "idx_courses_name", "table": "courses", "sql": "CREATE INDEX idx_courses_name ON courses (course_name)"},
                    {"name": "idx_courses_semester", "table": "courses", "sql": "CREATE INDEX idx_courses_semester ON courses (semester)"}
                ]
            },
            InitOrder.ENROLLMENTS: {
                "name": "enrollments",
                "create_sql": """
                    CREATE TABLE IF NOT EXISTS enrollments (
                        id              VARCHAR(36) PRIMARY KEY,
                        user_id         VARCHAR(36) NOT NULL,
                        course_id       VARCHAR(36) NOT NULL,
                        enrollment_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status          VARCHAR(20) DEFAULT 'active',
                        UNIQUE KEY idx_enrollments_unique (user_id, course_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """,
                "indexes": [
                    {"name": "idx_enrollments_user", "table": "enrollments", "sql": "CREATE INDEX idx_enrollments_user ON enrollments (user_id)"},
                    {"name": "idx_enrollments_course", "table": "enrollments", "sql": "CREATE INDEX idx_enrollments_course ON enrollments (course_id)"}
                ]
            },
            InitOrder.BOOKS: {
                "name": "books",
                "create_sql": """
                    CREATE TABLE IF NOT EXISTS books (
                        id              VARCHAR(36) PRIMARY KEY,
                        isbn            VARCHAR(20) UNIQUE,
                        title           VARCHAR(200) NOT NULL,
                        subtitle        VARCHAR(200) DEFAULT '',
                        author          VARCHAR(200) NOT NULL,
                        translator      VARCHAR(200) DEFAULT '',
                        publisher       VARCHAR(100) NOT NULL,
                        publish_date    VARCHAR(20) DEFAULT '',
                        category        VARCHAR(50) DEFAULT '',
                        summary         TEXT,
                        table_of_contents TEXT,
                        cover           VARCHAR(500) DEFAULT '',
                        file_url        VARCHAR(500) DEFAULT '',
                        created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """,
                "indexes": [
                    {"name": "idx_books_isbn", "table": "books", "sql": "CREATE INDEX idx_books_isbn ON books (isbn)"},
                    {"name": "idx_books_title", "table": "books", "sql": "CREATE INDEX idx_books_title ON books (title)"},
                    {"name": "idx_books_category", "table": "books", "sql": "CREATE INDEX idx_books_category ON books (category)"}
                ]
            },
            InitOrder.CONVERSATIONS: {
                "name": "conversations",
                "create_sql": """
                    CREATE TABLE IF NOT EXISTS conversations (
                        id              VARCHAR(36) PRIMARY KEY,
                        user_id         VARCHAR(36) NOT NULL,
                        title           VARCHAR(200),
                        current_mode    VARCHAR(20) DEFAULT 'knowledge',
                        created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        message_count   INT DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """,
                "indexes": [
                    {"name": "idx_conversations_user", "table": "conversations", "sql": "CREATE INDEX idx_conversations_user ON conversations (user_id)"}
                ]
            },
            InitOrder.MESSAGES: {
                "name": "messages",
                "create_sql": """
                    CREATE TABLE IF NOT EXISTS messages (
                        id              VARCHAR(36) PRIMARY KEY,
                        conversation_id VARCHAR(36) NOT NULL,
                        role            VARCHAR(20) NOT NULL,
                        content         TEXT NOT NULL,
                        agent_used      VARCHAR(50),
                        reasoning_steps TEXT,
                        `references`   JSON,
                        workflow_details JSON,
                        created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """,
                "indexes": [
                    {"name": "idx_messages_conversation", "table": "messages", "sql": "CREATE INDEX idx_messages_conversation ON messages (conversation_id)"}
                ]
            },
            InitOrder.MESSAGE_REFERENCES: {
                "name": "message_references",
                "create_sql": """
                    CREATE TABLE IF NOT EXISTS message_references (
                        id              VARCHAR(36) PRIMARY KEY,
                        message_id      VARCHAR(36) NOT NULL,
                        knowledge_id    VARCHAR(64) NOT NULL,
                        title           VARCHAR(200) DEFAULT '',
                        source_file     VARCHAR(500) DEFAULT '',
                        original_doc    VARCHAR(200) DEFAULT '',
                        course          VARCHAR(100) DEFAULT '',
                        score           DECIMAL(5,3) DEFAULT 0,
                        created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """,
                "indexes": [
                    {"name": "idx_message_refs_message", "table": "message_references", "sql": "CREATE INDEX idx_message_refs_message ON message_references (message_id)"},
                    {"name": "idx_message_refs_knowledge", "table": "message_references", "sql": "CREATE INDEX idx_message_refs_knowledge ON message_references (knowledge_id)"}
                ]
            },
            InitOrder.LEARNING_RECORDS: {
                "name": "learning_records",
                "create_sql": """
                    CREATE TABLE IF NOT EXISTS learning_records (
                        id                  VARCHAR(36) PRIMARY KEY,
                        user_id             VARCHAR(36) NOT NULL,
                        knowledge_point_id  VARCHAR(64),
                        action              VARCHAR(20) NOT NULL,
                        duration            INT DEFAULT 0,
                        created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """,
                "indexes": [
                    {"name": "idx_learning_user", "table": "learning_records", "sql": "CREATE INDEX idx_learning_user ON learning_records (user_id, created_at)"},
                    {"name": "idx_learning_knowledge", "table": "learning_records", "sql": "CREATE INDEX idx_learning_knowledge ON learning_records (knowledge_point_id)"}
                ]
            },
            InitOrder.KNOWLEDGE_COLLECTIONS: {
                "name": "knowledge_collections",
                "create_sql": """
                    CREATE TABLE IF NOT EXISTS knowledge_collections (
                        id                  VARCHAR(36) PRIMARY KEY,
                        user_id             VARCHAR(36) NOT NULL,
                        knowledge_point_id  VARCHAR(64) NOT NULL,
                        folder              VARCHAR(50) DEFAULT '默认收藏夹',
                        created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
                        note                VARCHAR(500) DEFAULT '',
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        UNIQUE KEY idx_collections_unique (user_id, knowledge_point_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """,
                "indexes": [
                    {"name": "idx_collections_user", "table": "knowledge_collections", "sql": "CREATE INDEX idx_collections_user ON knowledge_collections (user_id)"}
                ]
            }
        }

    async def verify_tables(self) -> Dict[str, bool]:
        """
        验证所有表是否存在

        Returns:
            Dict: 表名到存在状态的映射
        """
        result = {}
        schemas = self._get_all_schemas()
        
        for order in schemas.values():
            table_name = order["name"]
            try:
                row = await fetchrow_sql(
                    "SELECT COUNT(*) as count FROM information_schema.tables "
                    "WHERE table_schema = DATABASE() AND table_name = %s",
                    (table_name,)
                )
                result[table_name] = row["count"] > 0 if row else False
            except Exception as e:
                logger.error(f"验证表 {table_name} 失败: {str(e)}")
                result[table_name] = False
        
        return result

    async def drop_all_tables(self) -> bool:
        """
        删除所有表（谨慎使用）

        Returns:
            bool: 是否成功
        """
        try:
            tables = ["knowledge_collections", "learning_records", "message_references", "messages", 
                     "conversations", "books", "enrollments", "courses", "users"]
            
            pool = await get_pool()
            conn = await pool.acquire()
            try:
                async with conn.cursor() as cur:
                    await cur.execute("SET FOREIGN_KEY_CHECKS = 0")
                    
                    for table in tables:
                        try:
                            await cur.execute(f"DROP TABLE IF EXISTS {table}")
                            logger.info(f"表 {table} 已删除")
                        except Exception as e:
                            logger.warning(f"删除表 {table} 失败: {str(e)}")
                    
                    await cur.execute("SET FOREIGN_KEY_CHECKS = 1")
            finally:
                await pool.release(conn)
            
            self._initialized_tables.clear()
            return True
            
        except Exception as e:
            logger.error(f"删除所有表失败: {str(e)}")
            return False


_initializer: Optional[DatabaseInitializer] = None


async def get_initializer() -> DatabaseInitializer:
    """获取数据库初始化器实例"""
    global _initializer
    if _initializer is None:
        _initializer = DatabaseInitializer()
    return _initializer


async def initialize_database() -> Dict[str, Any]:
    """初始化数据库"""
    initializer = await get_initializer()
    return await initializer.initialize_all()


async def verify_database() -> Dict[str, bool]:
    """验证数据库表"""
    initializer = await get_initializer()
    return await initializer.verify_tables()
