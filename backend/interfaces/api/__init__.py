"""
API路由层
"""

from interfaces.api.chat_router import router as chat_router
from interfaces.api.knowledge_router import router as knowledge_router
from interfaces.api.learning_router import router as learning_router
from interfaces.api.auth_router import router as auth_router
from interfaces.api.upload_router import router as upload_router
from interfaces.api.agent_router import router as agent_router
from interfaces.api.admin_router import router as admin_router

__all__ = ["chat_router", "knowledge_router", "learning_router", "auth_router", "upload_router", "agent_router", "admin_router"]
