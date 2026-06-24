"""
异常处理模块

定义统一的异常类和异常处理机制。
"""

from typing import Optional, Dict, Any


class AppException(Exception):
    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="AUTH_ERROR",
            status_code=401,
            details=details
        )


class AuthorizationError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details
        )


class ValidationError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class ResourceNotFoundError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details=details
        )


class ConflictError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
            details=details
        )


class RateLimitError(AppException):
    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(
            message=message,
            code="RATE_LIMITED",
            status_code=429,
            details={"retry_after": retry_after}
        )


class DatabaseError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500,
            details=details
        )


class ExternalServiceError(AppException):
    def __init__(self, message: str, service: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="EXTERNAL_SERVICE_ERROR",
            status_code=503,
            details={"service": service, **(details or {})}
        )


def handle_exception(e: Exception) -> Dict[str, Any]:
    if isinstance(e, AppException):
        return {
            "error": e.code,
            "message": e.message,
            "details": e.details,
            "status_code": e.status_code
        }
    else:
        return {
            "error": "INTERNAL_ERROR",
            "message": "服务器内部错误，请稍后重试",
            "details": {"exception": str(type(e).__name__)},
            "status_code": 500
        }
