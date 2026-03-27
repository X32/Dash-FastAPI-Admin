"""
会话管理模块注册器
用于将模块集成到主应用中
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from . import conversation_router, conversation_exception_handler, ConversationException

logger = logging.getLogger(__name__)


def register_conversation_module(app: FastAPI, prefix: str = "/api/v1"):
    """
    注册会话管理模块
    
    Args:
        app: FastAPI应用实例
        prefix: API前缀，默认为 /api/v1
    """
    try:
        # 注册路由
        app.include_router(
            conversation_router,
            prefix=f"{prefix}/conversations",
            tags=["会话管理"]
        )
        
        # 注册异常处理器
        app.add_exception_handler(ConversationException, conversation_exception_handler)
        
        logger.info(f"会话管理模块注册成功，路由前缀: {prefix}/conversations")
        
    except Exception as e:
        logger.error(f"会话管理模块注册失败: {str(e)}")
        raise


def register_conversation_middleware(app: FastAPI):
    """
    注册会话管理相关的中间件
    
    Args:
        app: FastAPI应用实例
    """
    # 可以在这里添加特定的中间件配置
    pass


def get_conversation_module_info():
    """
    获取会话管理模块信息
    
    Returns:
        dict: 模块信息
    """
    return {
        "name": "会话管理模块",
        "version": "1.0.0",
        "description": "提供会话和消息的创建、查询、更新、删除等功能",
        "author": "系统管理员",
        "routes": [
            {
                "path": "/conversations",
                "method": "POST",
                "description": "创建会话"
            },
            {
                "path": "/conversations",
                "method": "GET", 
                "description": "获取会话列表"
            },
            {
                "path": "/conversations/{conversation_id}",
                "method": "GET",
                "description": "获取会话详情"
            },
            {
                "path": "/conversations/{conversation_id}",
                "method": "PUT",
                "description": "更新会话"
            },
            {
                "path": "/conversations/{conversation_id}",
                "method": "DELETE",
                "description": "删除会话"
            },
            {
                "path": "/conversations/{conversation_id}/messages",
                "method": "POST",
                "description": "创建消息"
            },
            {
                "path": "/conversations/{conversation_id}/messages/{message_id}",
                "method": "PUT",
                "description": "更新消息"
            },
            {
                "path": "/conversations/{conversation_id}/messages/{message_id}",
                "method": "DELETE",
                "description": "删除消息"
            }
        ]
    }