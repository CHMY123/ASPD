"""
单元测试 - 验证器

测试输入验证工具函数。
"""

import pytest
from common.validators import Validators


class TestValidators:
    def test_is_email_valid(self):
        assert Validators.is_email("test@example.com") is True
        assert Validators.is_email("user.name@domain.org") is True
        assert Validators.is_email("a@b.co") is True

    def test_is_email_invalid(self):
        assert Validators.is_email("invalid-email") is False
        assert Validators.is_email("@no-local.com") is False
        assert Validators.is_email("no-at-sign.com") is False
        assert Validators.is_email("") is False

    def test_is_username_valid(self):
        assert Validators.is_username("user123") is True
        assert Validators.is_username("test_user") is True
        assert Validators.is_username("abc") is True

    def test_is_username_invalid(self):
        assert Validators.is_username("ab") is False
        assert Validators.is_username("user@name") is False
        assert Validators.is_username("") is False

    def test_is_password_strong(self):
        assert Validators.is_password_strong("Password123") is True
        assert Validators.is_password_strong("MyPass99") is True

    def test_is_password_weak(self):
        assert Validators.is_password_strong("weak") is False
        assert Validators.is_password_strong("alllowercase1") is False
        assert Validators.is_password_strong("ALLUPPERCASE1") is False
        assert Validators.is_password_strong("NoNumbers") is False

    def test_is_uuid_valid(self):
        assert Validators.is_uuid("550e8400-e29b-41d4-a716-446655440000") is True
        assert Validators.is_uuid("550E8400-E29B-41D4-A716-446655440000") is True

    def test_is_uuid_invalid(self):
        assert Validators.is_uuid("invalid-uuid") is False
        assert Validators.is_uuid("550e8400-e29b-41d4-a716") is False

    def test_validate_email(self):
        assert Validators.validate_email("test@example.com") is None
        assert Validators.validate_email("") == "邮箱不能为空"
        assert Validators.validate_email("invalid") == "无效的邮箱格式"

    def test_validate_username(self):
        assert Validators.validate_username("testuser") is None
        assert Validators.validate_username("ab") == "用户名至少需要3个字符"
        assert Validators.validate_username("a" * 21) == "用户名最多允许20个字符"
        assert Validators.validate_username("user@name") == "用户名只能包含字母、数字和下划线"

    def test_validate_password(self):
        assert Validators.validate_password("Password123") is None
        assert Validators.validate_password("short") == "密码至少需要8个字符"
        assert Validators.validate_password("alllowercase1") == "密码需要包含大写字母"
        assert Validators.validate_password("ALLUPPERCASE1") == "密码需要包含小写字母"
        assert Validators.validate_password("NoNumbersHere") == "密码需要包含数字"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
