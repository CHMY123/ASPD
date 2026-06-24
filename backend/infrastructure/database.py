"""
数据库连接管理 (Database Connection Management)

管理TiDB Cloud数据库异步连接池。
"""

import asyncio
from typing import Optional
import aiomysql
import ssl
from config import DATABASE_URL

_pool: Optional[aiomysql.Pool] = None


async def get_pool() -> aiomysql.Pool:
    """
    获取数据库连接池

    如果连接池不存在，则创建新的连接池。

    Returns:
        aiomysql.Pool: 数据库连接池实例
    """
    global _pool
    if _pool is None:
        # 解析数据库URL
        # 格式: mysql+pymysql://username:password@host:port/database
        import urllib.parse
        parsed = urllib.parse.urlparse(DATABASE_URL)
        
        # 创建SSL上下文（TiDB Cloud要求SSL连接）
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        _pool = await aiomysql.create_pool(
            host=parsed.hostname,
            port=parsed.port or 4000,
            user=parsed.username,
            password=parsed.password,
            db=parsed.path.lstrip('/'),
            minsize=5,
            maxsize=20,
            connect_timeout=60,
            autocommit=True,
            charset='utf8mb4',
            ssl=ssl_context
        )
    return _pool


async def init_database() -> None:
    """
    初始化数据库

    创建连接池并验证连接。
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT VERSION()")
            version = await cur.fetchone()
            print(f"Database connected: {version[0]}")


async def close_database() -> None:
    """
    关闭数据库连接池
    """
    global _pool
    if _pool is not None:
        _pool.close()
        await _pool.wait_closed()
        _pool = None


async def execute_sql(sql: str, *args) -> int:
    """
    执行SQL语句

    Args:
        sql: SQL语句
        *args: 参数

    Returns:
        int: 影响的行数
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, args)
            return cur.rowcount


async def fetch_sql(sql: str, *args) -> list:
    """
    查询SQL

    Args:
        sql: SQL语句
        *args: 参数

    Returns:
        list: 查询结果列表
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql, args)
            result = await cur.fetchall()
            return result


async def fetchrow_sql(sql: str, *args) -> Optional[dict]:
    """
    查询单行SQL

    Args:
        sql: SQL语句
        *args: 参数

    Returns:
        Optional[dict]: 查询结果
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql, args)
            result = await cur.fetchone()
            return result


async def fetchval_sql(sql: str, *args):
    """
    查询单个值SQL

    Args:
        sql: SQL语句
        *args: 参数

    Returns:
        查询结果
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, args)
            result = await cur.fetchone()
            return result[0] if result else None


class DatabaseManager:
    """
    数据库管理器

    提供数据库操作的上下文管理器。
    """

    def __init__(self):
        self.pool: Optional[aiomysql.Pool] = None
        self.conn = None

    async def __aenter__(self):
        """进入上下文"""
        self.pool = await get_pool()
        self.conn = await self.pool.acquire()
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if self.conn:
            await self.pool.release(self.conn)