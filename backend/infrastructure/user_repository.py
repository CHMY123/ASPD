"""
用户仓储实现 (MySQL User Repository)

基于MySQL实现用户数据访问。
"""

import logging
from typing import List, Optional
from datetime import datetime
from domain.user.entity import User, UserRole
from domain.user.repository import UserRepository
from infrastructure.database import execute_sql, fetch_sql, fetchrow_sql

logger = logging.getLogger(__name__)


class PgUserRepository(UserRepository):
    """
    MySQL用户仓储实现
    """

    async def init_schema(self) -> None:
        """初始化数据库模式（已移至database_init.py统一处理）"""
        logger.info("用户表初始化已由DatabaseInitializer统一处理")

    async def create(self, user: User) -> bool:
        """创建用户"""
        try:
            await execute_sql("""
                INSERT INTO users
                (id, username, email, password_hash, role, is_active, created_at, updated_at, real_name, student_id, major, grade, avatar)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                user.id,
                user.username,
                user.email,
                user.password_hash,
                user.role.value,
                user.is_active,
                user.created_at,
                user.updated_at,
                user.real_name,
                user.student_id,
                user.major,
                user.grade,
                user.avatar
            )
            return True
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            return False

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        row = await fetchrow_sql(
            "SELECT * FROM users WHERE id = %s",
            user_id
        )

        if not row:
            return None

        return self._row_to_user(row)

    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        row = await fetchrow_sql(
            "SELECT * FROM users WHERE username = %s",
            username
        )

        if not row:
            return None

        return self._row_to_user(row)

    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        row = await fetchrow_sql(
            "SELECT * FROM users WHERE email = %s",
            email
        )

        if not row:
            return None

        return self._row_to_user(row)

    async def update(self, user: User) -> bool:
        """更新用户"""
        try:
            await execute_sql("""
                UPDATE users SET
                    username = %s,
                    email = %s,
                    password_hash = %s,
                    role = %s,
                    is_active = %s,
                    updated_at = %s,
                    real_name = %s,
                    student_id = %s,
                    major = %s,
                    grade = %s,
                    avatar = %s
                WHERE id = %s
            """,
                user.username,
                user.email,
                user.password_hash,
                user.role.value,
                user.is_active,
                user.updated_at,
                user.real_name,
                user.student_id,
                user.major,
                user.grade,
                user.avatar,
                user.id
            )
            return True
        except Exception as e:
            logger.error(f"更新用户失败: {e}")
            return False

    async def delete(self, user_id: str) -> bool:
        """删除用户"""
        try:
            await execute_sql(
                "DELETE FROM users WHERE id = %s",
                user_id
            )
            return True
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            return False

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """用户认证"""
        user = await self.get_by_username(username)
        
        if user and user.verify_password(password) and user.is_active:
            user.updated_at = datetime.now()
            await self.update(user)
            return user
        
        return None

    async def exists(self, user_id: str) -> bool:
        """检查用户是否存在"""
        row = await fetchrow_sql(
            "SELECT 1 FROM users WHERE id = %s",
            user_id
        )
        return row is not None

    async def username_exists(self, username: str) -> bool:
        """检查用户名是否存在"""
        row = await fetchrow_sql(
            "SELECT 1 FROM users WHERE username = %s",
            username
        )
        return row is not None

    async def email_exists(self, email: str) -> bool:
        """检查邮箱是否存在"""
        row = await fetchrow_sql(
            "SELECT 1 FROM users WHERE email = %s",
            email
        )
        return row is not None

    async def count(self) -> int:
        """获取用户总数"""
        result = await fetchrow_sql(
            "SELECT COUNT(*) as count FROM users"
        )
        return result["count"] if result else 0

    def _row_to_user(self, row: dict) -> User:
        """将数据库行转换为用户实体"""
        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            role=UserRole(row["role"]),
            is_active=row.get("is_active", True),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            real_name=row.get("real_name", ""),
            student_id=row.get("student_id", ""),
            major=row.get("major", ""),
            grade=row.get("grade", ""),
            avatar=row.get("avatar", "")
        )
