"""
认证API路由 (Authentication API Router)

提供用户注册、登录、令牌刷新等接口。
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from application.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["认证"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 全局服务实例
_auth_service: AuthService = None


def set_auth_service(auth_service: AuthService):
    """设置认证服务"""
    global _auth_service
    _auth_service = auth_service


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """获取当前登录用户"""
    if not _auth_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="认证服务未初始化"
        )

    user = await _auth_service.validate_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user.to_dict()


class RegisterRequest(BaseModel):
    """注册请求模型"""
    username: str
    email: EmailStr
    password: str
    real_name: str
    role: Optional[str] = "student"


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""
    old_password: str
    new_password: str


class UpdateProfileRequest(BaseModel):
    """更新用户资料请求模型"""
    real_name: Optional[str] = None
    student_id: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
    avatar: Optional[str] = None


@router.post("/register")
async def register(request: RegisterRequest):
    """
    用户注册
    
    创建新用户账户
    """
    if not _auth_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="认证服务未初始化"
        )

    from domain.user.entity import UserRole
    
    role = UserRole(request.role.lower()) if request.role else UserRole.STUDENT
    
    result = await _auth_service.register(
        username=request.username,
        email=request.email,
        password=request.password,
        role=role,
        real_name=request.real_name
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

    return {
        "success": True,
        "message": result["message"],
        "user": {
            "id": result["user"]["id"],
            "username": result["user"]["username"],
            "email": result["user"]["email"],
            "role": result["user"]["role"]
        }
    }


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录
    
    使用OAuth2密码模式进行认证
    """
    if not _auth_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="认证服务未初始化"
        )

    result = await _auth_service.login(
        username=form_data.username,
        password=form_data.password
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["message"],
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "token_type": "bearer",
        "user": {
            "id": result["user"]["id"],
            "username": result["user"]["username"],
            "email": result["user"]["email"],
            "role": result["user"]["role"],
            "real_name": result["user"].get("real_name", ""),
            "avatar": result["user"].get("avatar", "")
        }
    }


@router.post("/login/json")
async def login_json(request: LoginRequest):
    """
    用户登录（JSON格式）
    
    使用JSON格式进行认证
    """
    if not _auth_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="认证服务未初始化"
        )

    result = await _auth_service.login(
        username=request.username,
        password=request.password
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["message"],
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "token_type": "bearer",
        "user": {
            "id": result["user"]["id"],
            "username": result["user"]["username"],
            "email": result["user"]["email"],
            "role": result["user"]["role"],
            "real_name": result["user"].get("real_name", ""),
            "avatar": result["user"].get("avatar", "")
        }
    }


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """
    刷新访问令牌
    """
    if not _auth_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="认证服务未初始化"
        )

    result = await _auth_service.refresh_token(request.refresh_token)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["message"]
        )

    return {
        "access_token": result["access_token"],
        "token_type": result["token_type"]
    }


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    if hasattr(current_user, 'to_dict'):
        return current_user.to_dict()
    return current_user


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    修改密码
    """
    if not _auth_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="认证服务未初始化"
        )

    result = await _auth_service.change_password(
        user_id=current_user["id"],
        old_password=request.old_password,
        new_password=request.new_password
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

    return {"success": True, "message": result["message"]}


@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """
    用户登出
    
    将令牌添加到黑名单使其失效，客户端应删除本地存储的令牌
    """
    if not _auth_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="认证服务未初始化"
        )

    result = await _auth_service.logout(token, current_user["id"])

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

    return {"success": True, "message": result["message"]}


@router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    更新用户资料
    """
    if not _auth_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="认证服务未初始化"
        )

    result = await _auth_service.update_profile(
        user_id=current_user["id"],
        real_name=request.real_name,
        student_id=request.student_id,
        major=request.major,
        grade=request.grade,
        avatar=request.avatar
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

    return result["user"]