"""
认证服务 (Authentication Service)

提供用户注册、登录和JWT令牌管理功能。
"""

from typing import Optional, Dict, Any, Set
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from domain.user.entity import User, UserRole
from domain.user.repository import UserRepository
from common.logger import logger
from common.validators import Validators

SECRET_KEY = "your-secret-key-change-in-production-keep-it-safe"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
REFRESH_TOKEN_EXPIRE_DAYS = 7

# 令牌黑名单（用于登出功能）
_token_blacklist: Set[str] = set()


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def initialize(self):
        await self.user_repository.init_schema()
        logger.info("AuthService initialized")

    async def register(
        self,
        username: str,
        email: str,
        password: str,
        role: UserRole = UserRole.STUDENT,
        real_name: str = ""
    ) -> Dict[str, Any]:
        username_error = Validators.validate_username(username)
        if username_error:
            logger.warning(f"Username validation failed: {username_error}")
            return {"success": False, "message": username_error}

        email_error = Validators.validate_email(email)
        if email_error:
            logger.warning(f"Email validation failed: {email_error}")
            return {"success": False, "message": email_error}

        password_error = Validators.validate_password(password)
        if password_error:
            logger.warning(f"Password validation failed")
            return {"success": False, "message": password_error}

        if not real_name:
            logger.warning(f"Real name validation failed")
            return {"success": False, "message": "真实姓名不能为空"}

        if await self.user_repository.username_exists(username):
            logger.warning(f"Username already exists: {username}")
            return {"success": False, "message": "用户名已存在"}

        if await self.user_repository.email_exists(email):
            logger.warning(f"Email already exists: {email}")
            return {"success": False, "message": "邮箱已被注册"}

        user = User.create_student(username, email, password)
        user.role = role
        user.real_name = real_name

        success = await self.user_repository.create(user)

        if success:
            logger.info(f"User registered successfully: {username}")
            return {
                "success": True,
                "message": "注册成功",
                "user": user.to_dict()
            }
        else:
            logger.error(f"Failed to create user: {username}")
            return {"success": False, "message": "注册失败，请稍后重试"}

    async def login(self, username: str, password: str) -> Dict[str, Any]:
        if not username or not password:
            return {"success": False, "message": "用户名和密码不能为空"}

        user = await self.user_repository.authenticate(username, password)

        if not user:
            logger.warning(f"Failed login attempt for username: {username}")
            return {"success": False, "message": "用户名或密码错误"}

        access_token = self.create_access_token(user.id)
        refresh_token = self.create_refresh_token(user.id)

        logger.info(f"User logged in successfully: {username}")
        return {
            "success": True,
            "message": "登录成功",
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        if not refresh_token:
            return {"success": False, "message": "刷新令牌不能为空"}

        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")

            if user_id is None:
                return {"success": False, "message": "无效的刷新令牌"}

            user = await self.user_repository.get_by_id(user_id)

            if not user or not user.is_active():
                return {"success": False, "message": "用户不存在或已禁用"}

            access_token = self.create_access_token(user_id)

            logger.info(f"Token refreshed for user: {user_id}")
            return {
                "success": True,
                "message": "令牌刷新成功",
                "access_token": access_token,
                "token_type": "bearer"
            }

        except JWTError as e:
            logger.error(f"JWT error during token refresh: {str(e)}")
            return {"success": False, "message": "无效的刷新令牌"}

    async def validate_token(self, token: str) -> Optional[User]:
        if not token:
            return None

        # 检查令牌是否在黑名单中
        if self.is_token_blacklisted(token):
            logger.warning("Token is blacklisted")
            return None

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")

            if user_id is None:
                return None

            user = await self.user_repository.get_by_id(user_id)

            if user and user.is_active:
                return user

            return None

        except JWTError as e:
            logger.error(f"JWT validation error: {str(e)}")
            return None

    def create_access_token(self, user_id: str) -> str:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta

        payload = {
            "sub": user_id,
            "exp": expire,
            "type": "access"
        }

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def create_refresh_token(self, user_id: str) -> str:
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        expire = datetime.utcnow() + expires_delta

        payload = {
            "sub": user_id,
            "exp": expire,
            "type": "refresh"
        }

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    async def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> Dict[str, Any]:
        if not old_password or not new_password:
            return {"success": False, "message": "密码不能为空"}

        password_error = Validators.validate_password(new_password)
        if password_error:
            return {"success": False, "message": password_error}

        user = await self.user_repository.get_by_id(user_id)

        if not user:
            logger.warning(f"User not found for password change: {user_id}")
            return {"success": False, "message": "用户不存在"}

        if not user.verify_password(old_password):
            logger.warning(f"Old password mismatch for user: {user_id}")
            return {"success": False, "message": "旧密码错误"}

        user.password_hash = User.hash_password(new_password)
        user.updated_at = datetime.now()

        success = await self.user_repository.update(user)

        if success:
            logger.info(f"Password changed successfully for user: {user_id}")
            return {"success": True, "message": "密码修改成功"}
        else:
            logger.error(f"Failed to update password for user: {user_id}")
            return {"success": False, "message": "密码修改失败"}

    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        user = await self.user_repository.get_by_id(user_id)

        if user:
            return user.to_dict()

        return None

    async def update_profile(
        self,
        user_id: str,
        real_name: Optional[str] = None,
        student_id: Optional[str] = None,
        major: Optional[str] = None,
        grade: Optional[str] = None,
        avatar: Optional[str] = None
    ) -> Dict[str, Any]:
        user = await self.user_repository.get_by_id(user_id)

        if not user:
            logger.warning(f"User not found for profile update: {user_id}")
            return {"success": False, "message": "用户不存在"}

        if real_name is not None:
            user.real_name = real_name
        
        if student_id is not None:
            user.student_id = student_id
        
        if major is not None:
            user.major = major
        
        if grade is not None:
            user.grade = grade
        
        if avatar is not None:
            user.avatar = avatar
        
        user.updated_at = datetime.now()

        success = await self.user_repository.update(user)

        if success:
            logger.info(f"Profile updated successfully for user: {user_id}")
            return {"success": True, "message": "资料更新成功", "user": user.to_dict()}
        else:
            logger.error(f"Failed to update profile for user: {user_id}")
            return {"success": False, "message": "资料更新失败"}

    async def logout(self, token: str, user_id: str) -> Dict[str, Any]:
        """
        用户登出
        
        将令牌添加到黑名单，使其失效
        """
        if not token:
            return {"success": False, "message": "令牌不能为空"}
        
        # 将令牌添加到黑名单
        _token_blacklist.add(token)
        
        logger.info(f"User logged out successfully: {user_id}")
        return {"success": True, "message": "登出成功"}

    def is_token_blacklisted(self, token: str) -> bool:
        """
        检查令牌是否在黑名单中
        """
        return token in _token_blacklist

    def cleanup_blacklist(self):
        """
        清理黑名单中过期的令牌
        
        定期调用此方法以清理过期令牌
        """
        current_time = datetime.utcnow()
        expired_tokens = []
        
        for token in _token_blacklist:
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                exp = payload.get("exp")
                if exp and datetime.fromtimestamp(exp) < current_time:
                    expired_tokens.append(token)
            except JWTError:
                # 无效令牌也应该移除
                expired_tokens.append(token)
        
        for token in expired_tokens:
            _token_blacklist.discard(token)
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired tokens from blacklist")
