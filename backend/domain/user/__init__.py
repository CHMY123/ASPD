"""
用户领域 (User Domain)

包含用户实体定义和仓储接口。
"""

from domain.user.entity import User, UserRole
from domain.user.repository import UserRepository

__all__ = ["User", "UserRole", "UserRepository"]
