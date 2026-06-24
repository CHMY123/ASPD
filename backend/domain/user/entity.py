"""
用户实体 (User Entity)

定义用户的数据结构和角色。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import bcrypt


class UserRole(Enum):
    """用户角色枚举"""
    STUDENT = "student"
    ASSISTANT = "assistant"
    TEACHER = "teacher"
    ADMIN = "admin"


@dataclass
class User:
    """
    用户实体

    Attributes:
        id: 用户唯一标识符
        username: 用户名
        email: 邮箱
        password_hash: 密码哈希
        role: 用户角色
        is_active: 是否激活
        created_at: 创建时间
        updated_at: 更新时间
        real_name: 真实姓名
        student_id: 学号
        major: 专业
        grade: 年级
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    password_hash: str = ""
    role: UserRole = UserRole.STUDENT
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    real_name: str = ""
    student_id: str = ""
    major: str = ""
    grade: str = ""
    avatar: str = ""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        对密码进行哈希（使用bcrypt算法）

        Args:
            password: 原始密码

        Returns:
            str: 哈希后的密码
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(self, password: str) -> bool:
        """
        验证密码

        Args:
            password: 待验证的密码

        Returns:
            bool: 是否匹配
        """
        try:
            return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))
        except Exception:
            return False

    def can_manage_knowledge(self) -> bool:
        """
        检查是否有知识库管理权限

        Returns:
            bool: 是否有权限
        """
        return self.role in [UserRole.TEACHER, UserRole.ASSISTANT, UserRole.ADMIN]

    def can_manage_users(self) -> bool:
        """
        检查是否有用户管理权限

        Returns:
            bool: 是否有权限
        """
        return self.role == UserRole.ADMIN

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        转换为字典格式

        Args:
            include_sensitive: 是否包含敏感信息

        Returns:
            dict: 字典表示
        """
        result = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "real_name": self.real_name,
            "student_id": self.student_id,
            "major": self.major,
            "grade": self.grade,
            "avatar": self.avatar
        }
        if include_sensitive:
            result["password_hash"] = self.password_hash
        return result

    @classmethod
    def create_student(cls, username: str, email: str, password: str) -> "User":
        """
        创建学生用户

        Args:
            username: 用户名
            email: 邮箱
            password: 密码

        Returns:
            User: 用户实例
        """
        return cls(
            username=username,
            email=email,
            password_hash=cls.hash_password(password),
            role=UserRole.STUDENT,
        )

    @classmethod
    def create_teacher(
        cls,
        username: str,
        email: str,
        password: str
    ) -> "User":
        """
        创建教师用户

        Args:
            username: 用户名
            email: 邮箱
            password: 密码

        Returns:
            User: 用户实例
        """
        return cls(
            username=username,
            email=email,
            password_hash=cls.hash_password(password),
            role=UserRole.TEACHER,
        )
