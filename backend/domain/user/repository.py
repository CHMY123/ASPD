"""
用户仓储接口 (UserRepository Interface)

定义用户数据访问的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.user.entity import User


class UserRepository(ABC):
    """
    用户仓储接口

    定义用户数据访问的抽象接口。
    """

    @abstractmethod
    async def init_schema(self) -> None:
        """
        初始化数据库模式
        """
        pass

    @abstractmethod
    async def create(self, user: User) -> bool:
        """
        创建用户

        Args:
            user: 用户实体

        Returns:
            bool: 是否创建成功
        """
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        根据ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            Optional[User]: 用户实体，不存在则返回None
        """
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户

        Args:
            username: 用户名

        Returns:
            Optional[User]: 用户实体，不存在则返回None
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户

        Args:
            email: 邮箱

        Returns:
            Optional[User]: 用户实体，不存在则返回None
        """
        pass

    @abstractmethod
    async def update(self, user: User) -> bool:
        """
        更新用户

        Args:
            user: 用户实体

        Returns:
            bool: 是否更新成功
        """
        pass

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """
        删除用户

        Args:
            user_id: 用户ID

        Returns:
            bool: 是否删除成功
        """
        pass

    @abstractmethod
    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        用户认证

        Args:
            username: 用户名
            password: 密码

        Returns:
            Optional[User]: 认证成功返回用户实体，失败返回None
        """
        pass

    @abstractmethod
    async def exists(self, user_id: str) -> bool:
        """
        检查用户是否存在

        Args:
            user_id: 用户ID

        Returns:
            bool: 是否存在
        """
        pass

    @abstractmethod
    async def username_exists(self, username: str) -> bool:
        """
        检查用户名是否存在

        Args:
            username: 用户名

        Returns:
            bool: 是否存在
        """
        pass

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """
        检查邮箱是否存在

        Args:
            email: 邮箱

        Returns:
            bool: 是否存在
        """
        pass

    @abstractmethod
    async def count(self) -> int:
        """
        获取用户总数

        Returns:
            int: 用户数量
        """
        pass
