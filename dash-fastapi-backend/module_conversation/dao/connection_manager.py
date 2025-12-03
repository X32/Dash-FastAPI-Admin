#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话管理模块数据库连接管理器
集成连接池监控和性能优化功能
"""

import time
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from config.database import async_engine, AsyncSessionLocal
from config.env import DataBaseConfig


class ConnectionPoolStats:
    """连接池统计信息"""
    
    def __init__(self):
        self.total_connections = 0
        self.active_connections = 0
        self.idle_connections = 0
        self.total_queries = 0
        self.failed_queries = 0
        self.avg_query_time = 0.0
        self.slow_queries = 0
        self.start_time = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        uptime = time.time() - self.start_time
        return {
            'total_connections': self.total_connections,
            'active_connections': self.active_connections,
            'idle_connections': self.idle_connections,
            'total_queries': self.total_queries,
            'failed_queries': self.failed_queries,
            'avg_query_time': round(self.avg_query_time, 4),
            'slow_queries': self.slow_queries,
            'uptime_seconds': round(uptime, 2),
            'qps': round(self.total_queries / max(uptime, 1), 2)
        }


class ConversationConnectionManager:
    """会话管理模块数据库连接管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.stats = ConnectionPoolStats()
        self._setup_event_listeners()
        self.slow_query_threshold = 1.0  # 慢查询阈值（秒）
    
    def _setup_event_listeners(self):
        """设置SQLAlchemy事件监听器"""
        
        @event.listens_for(Engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            """连接建立事件"""
            self.stats.total_connections += 1
            self.stats.active_connections += 1
            self.logger.debug(f"数据库连接已建立，总连接数: {self.stats.total_connections}")
        
        @event.listens_for(Engine, "close")
        def on_close(dbapi_connection, connection_record):
            """连接关闭事件"""
            self.stats.active_connections = max(0, self.stats.active_connections - 1)
            self.logger.debug(f"数据库连接已关闭，活跃连接数: {self.stats.active_connections}")
        
        @event.listens_for(Engine, "checkout")
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
            """连接检出事件"""
            self.stats.active_connections += 1
            connection_record._checkout_time = time.time()
        
        @event.listens_for(Engine, "checkin")
        def on_checkin(dbapi_connection, connection_record):
            """连接归还事件"""
            self.stats.active_connections = max(0, self.stats.active_connections - 1)
            if hasattr(connection_record, '_checkout_time'):
                usage_time = time.time() - connection_record._checkout_time
                if usage_time > self.slow_query_threshold:
                    self.stats.slow_queries += 1
                    self.logger.warning(f"慢查询检测：连接使用时长 {usage_time:.2f}s")
        
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """查询执行前事件"""
            conn._query_start_time = time.time()
            self.logger.debug(f"执行SQL: {statement[:100]}...")
        
        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """查询执行后事件"""
            if hasattr(conn, '_query_start_time'):
                execution_time = time.time() - conn._query_start_time
                self.stats.total_queries += 1
                self.stats.avg_query_time = (
                    (self.stats.avg_query_time * (self.stats.total_queries - 1) + execution_time) 
                    / self.stats.total_queries
                )
                
                if execution_time > self.slow_query_threshold:
                    self.stats.slow_queries += 1
                    self.logger.warning(f"慢查询检测：SQL执行时长 {execution_time:.2f}s - {statement[:100]}...")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        return self.stats.to_dict()
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """获取SQLAlchemy引擎统计信息"""
        try:
            pool = async_engine.pool
            return {
                'pool_size': getattr(pool, 'size', 0),
                'checked_in_connections': getattr(pool, 'checked_in', 0),
                'checked_out_connections': getattr(pool, 'checked_out', 0),
                'overflow_connections': getattr(pool, 'overflow', 0),
                'pool_timeout': getattr(pool, 'timeout', 0),
                'pool_recycle': getattr(pool, 'recycle', 0),
                'pool_max_overflow': getattr(pool, 'max_overflow', 0)
            }
        except Exception as e:
            self.logger.error(f"获取引擎统计信息失败: {e}")
            return {}
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = ConnectionPoolStats()
        self.logger.info("连接池统计信息已重置")
    
    @asynccontextmanager
    async def get_session(self):
        """获取数据库会话（带监控）"""
        session: Optional[AsyncSession] = None
        try:
            async with AsyncSessionLocal() as session:
                yield session
        except Exception as e:
            self.stats.failed_queries += 1
            self.logger.error(f"数据库会话异常: {e}")
            raise
        finally:
            if session:
                await session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            async with self.get_session() as session:
                start_time = time.time()
                result = await session.execute(text("SELECT 1"))
                result.scalar()  # 移除await
                response_time = time.time() - start_time
                
                return {
                    'status': 'healthy',
                    'response_time': round(response_time, 4),
                    'stats': self.get_stats(),
                    'engine_stats': self.get_engine_stats(),
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }


# 全局连接管理器实例
connection_manager = ConversationConnectionManager()


async def get_managed_db():
    """获取带监控的数据库会话"""
    async with connection_manager.get_session() as session:
        yield session