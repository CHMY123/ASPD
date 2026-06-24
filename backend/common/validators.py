"""
请求验证模块

提供输入验证工具函数。
"""

import re
from typing import Optional, List


class Validators:
    @staticmethod
    def is_email(email: str) -> bool:
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    @staticmethod
    def is_username(username: str) -> bool:
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return re.match(pattern, username) is not None

    @staticmethod
    def is_password_strong(password: str) -> bool:
        if len(password) < 8:
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[0-9]', password):
            return False
        return True

    @staticmethod
    def is_uuid(uuid_str: str) -> bool:
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return re.match(pattern, uuid_str, re.IGNORECASE) is not None

    @staticmethod
    def is_positive_integer(value: int) -> bool:
        return isinstance(value, int) and value > 0

    @staticmethod
    def validate_email(email: str) -> Optional[str]:
        if not email:
            return "邮箱不能为空"
        if not Validators.is_email(email):
            return "无效的邮箱格式"
        return None

    @staticmethod
    def validate_username(username: str) -> Optional[str]:
        if not username:
            return "用户名不能为空"
        if len(username) < 3:
            return "用户名至少需要3个字符"
        if len(username) > 20:
            return "用户名最多允许20个字符"
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return "用户名只能包含字母、数字和下划线"
        return None

    @staticmethod
    def validate_password(password: str) -> Optional[str]:
        if not password:
            return "密码不能为空"
        if len(password) < 6:
            return "密码至少需要6个字符"
        return None

    @staticmethod
    def validate_page_params(page: int, page_size: int) -> List[str]:
        errors = []
        if not isinstance(page, int) or page < 1:
            errors.append("页码必须大于0")
        if not isinstance(page_size, int) or page_size < 1:
            errors.append("每页大小必须大于0")
        if isinstance(page_size, int) and page_size > 100:
            errors.append("每页大小不能超过100")
        return errors
