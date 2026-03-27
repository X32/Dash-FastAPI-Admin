"""
会话管理模块异常处理
"""
from .conversation_exception import (
    ConversationException,
    ConversationNotFoundException,
    MessageNotFoundException,
    MessageContentNotFoundException,
    PermissionDeniedException,
    InvalidConversationDataException,
    InvalidMessageDataException
)

from fastapi import Request
from fastapi.responses import JSONResponse
import traceback
import logging

logger = logging.getLogger(__name__)


async def conversation_exception_handler(request: Request, exc: ConversationException):
    """会话管理异常处理器"""
    logger.error(f"会话管理异常: {exc.detail}, 状态码: {exc.status_code}, 路径: {request.url.path}")
    logger.error(f"异常堆栈: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None,
            "success": False,
            "path": str(request.url.path),
            "method": request.method
        }
    )


__all__ = [
    "ConversationException",
    "ConversationNotFoundException", 
    "MessageNotFoundException",
    "MessageContentNotFoundException",
    "PermissionDeniedException",
    "InvalidConversationDataException",
    "InvalidMessageDataException",
    "conversation_exception_handler"
]