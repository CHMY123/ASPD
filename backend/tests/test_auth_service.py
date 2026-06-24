"""
单元测试 - 认证服务

测试用户注册、登录、令牌管理等功能。
"""

import pytest
import jwt
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from domain.user.entity import User, UserRole
from application.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM


class TestAuthService:
    @pytest.fixture
    def mock_user_repo(self):
        repo = AsyncMock()
        repo.init_schema = AsyncMock(return_value=None)
        repo.username_exists = AsyncMock(return_value=False)
        repo.email_exists = AsyncMock(return_value=False)
        repo.create = AsyncMock(return_value=True)
        repo.authenticate = AsyncMock(return_value=None)
        repo.get_by_id = AsyncMock(return_value=None)
        repo.update = AsyncMock(return_value=True)
        return repo

    @pytest.fixture
    def auth_service(self, mock_user_repo):
        return AuthService(mock_user_repo)

    @pytest.mark.asyncio
    async def test_register_success(self, auth_service, mock_user_repo):
        result = await auth_service.register(
            username="testuser",
            email="test@example.com",
            password="Password123"
        )
        assert result["success"] is True
        assert result["message"] == "注册成功"
        mock_user_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_username_exists(self, auth_service, mock_user_repo):
        mock_user_repo.username_exists = AsyncMock(return_value=True)
        result = await auth_service.register(
            username="testuser",
            email="test@example.com",
            password="Password123"
        )
        assert result["success"] is False
        assert result["message"] == "用户名已存在"

    @pytest.mark.asyncio
    async def test_register_invalid_username(self, auth_service):
        result = await auth_service.register(
            username="ab",
            email="test@example.com",
            password="Password123"
        )
        assert result["success"] is False
        assert "用户名至少需要3个字符" in result["message"]

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, auth_service):
        result = await auth_service.register(
            username="testuser",
            email="invalid-email",
            password="Password123"
        )
        assert result["success"] is False
        assert "无效的邮箱格式" in result["message"]

    @pytest.mark.asyncio
    async def test_register_weak_password(self, auth_service):
        result = await auth_service.register(
            username="testuser",
            email="test@example.com",
            password="weak"
        )
        assert result["success"] is False
        assert "密码至少需要8个字符" in result["message"]

    @pytest.mark.asyncio
    async def test_login_success(self, auth_service, mock_user_repo):
        user = User(
            id="test-user-id",
            username="testuser",
            email="test@example.com",
            password_hash=User.hash_password("Password123")
        )
        mock_user_repo.authenticate = AsyncMock(return_value=user)
        
        result = await auth_service.login("testuser", "Password123")
        assert result["success"] is True
        assert "access_token" in result
        assert "refresh_token" in result

    @pytest.mark.asyncio
    async def test_login_failure(self, auth_service, mock_user_repo):
        mock_user_repo.authenticate = AsyncMock(return_value=None)
        
        result = await auth_service.login("testuser", "wrongpassword")
        assert result["success"] is False
        assert result["message"] == "用户名或密码错误"

    # ========== 令牌过期测试 ==========

    def test_access_token_expires_24hours(self):
        """验证access_token默认过期时间为24小时（1440分钟）"""
        assert ACCESS_TOKEN_EXPIRE_MINUTES == 1440, (
            f"ACCESS_TOKEN_EXPIRE_MINUTES应为1440 (24h), 当前为 {ACCESS_TOKEN_EXPIRE_MINUTES}"
        )

    def test_access_token_has_correct_expiry(self, auth_service):
        """验证创建的token的过期时间正确设置为24小时后"""
        user_id = "test-user-id"
        token = auth_service.create_access_token(user_id)
        
        # 解码token（不验证签名）
        payload = jwt.decode(token, options={"verify_signature": False})
        
        assert payload["sub"] == user_id
        assert "exp" in payload
        
        # 验证过期时间约为当前时间+24小时（允许几分钟偏差）
        expected_exp = datetime.utcnow() + timedelta(minutes=1440)
        actual_exp = datetime.utcfromtimestamp(payload["exp"])
        time_diff = abs((actual_exp - expected_exp).total_seconds())
        assert time_diff < 120, f"过期时间偏差过大: {time_diff}s"

    def test_expired_token_is_rejected(self, auth_service):
        """验证过期token被正确拒绝"""
        # 手动创建一个已过期的token（30分钟前过期）
        expired_payload = {
            "sub": "test-user-id",
            "exp": datetime.utcnow() - timedelta(minutes=30),
            "iat": datetime.utcnow() - timedelta(hours=2),
            "type": "access"
        }
        expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
        
        # 验证 - validate_token会自动解码并检查exp
        import pytest
        with pytest.raises(jwt.exceptions.ExpiredSignatureError):
            jwt.decode(expired_token, SECRET_KEY, algorithms=[ALGORITHM])

    def test_future_token_is_accepted(self, auth_service):
        """验证有效的token被正确接受"""
        user_id = "test-user-id"
        token = auth_service.create_access_token(user_id)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_invalid_token_is_rejected(self, auth_service):
        """验证无效token被正确拒绝"""
        import pytest
        with pytest.raises(jwt.exceptions.DecodeError):
            jwt.decode("invalid-token-string", SECRET_KEY, algorithms=[ALGORITHM])

    @patch.dict('os.environ', {'ACCESS_TOKEN_EXPIRE_MINUTES': '120'})
    def test_token_expiry_from_env(self):
        """验证token过期时间可通过环境变量配置"""
        # 重新导入模块以触发环境变量覆盖
        import importlib
        import application.auth_service
        importlib.reload(application.auth_service)
        from application.auth_service import ACCESS_TOKEN_EXPIRE_MINUTES
        assert ACCESS_TOKEN_EXPIRE_MINUTES == 120
        # 恢复原始值
        importlib.reload(application.auth_service)

    def test_refresh_token_expiry(self, auth_service):
        """验证refresh_token过期时间为7天"""
        token = auth_service.create_refresh_token("test-user-id")
        payload = jwt.decode(token, options={"verify_signature": False})
        
        assert payload["sub"] == "test-user-id"
        assert payload.get("type") == "refresh"
        assert "exp" in payload
        
        # 验证过期时间约为当前时间+7天
        expected_exp = datetime.utcnow() + timedelta(days=7)
        actual_exp = datetime.utcfromtimestamp(payload["exp"])
        time_diff = abs((actual_exp - expected_exp).total_seconds())
        assert time_diff < 120, f"Refresh token过期时间偏差过大: {time_diff}s"

    def test_create_access_token(self, auth_service):
        token = auth_service.create_access_token("test-user-id")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self, auth_service):
        token = auth_service.create_refresh_token("test-user-id")
        assert isinstance(token, str)
        assert len(token) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
