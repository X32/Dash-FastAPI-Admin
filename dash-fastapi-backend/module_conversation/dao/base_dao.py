#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话管理模块数据库访问对象基类
集成连接池管理和性能优化功能
"""

from typing import Optional, Type, TypeVar, Generic, List, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from module_conversation.dao.connection_manager import connection_manager
from utils.log_util import logger

T = TypeVar('T')


class BaseConversationDAO(Generic[T]):
    """会话管理模块DAO基类"""
    
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
        self.logger = logger
    
    async def create(self, session: AsyncSession, **kwargs) -> T:
        """创建记录"""
        try:
            instance = self.model_class(**kwargs)
            session.add(instance)
            await session.flush()
            self.logger.info(f"创建{self.model_class.__name__}记录成功: {instance}")
            return instance
        except SQLAlchemyError as e:
            self.logger.error(f"创建{self.model_class.__name__}记录失败: {e}")
            raise
    
    async def get_by_id(self, session: AsyncSession, record_id: int) -> Optional[T]:
        """根据ID获取记录"""
        try:
            result = await session.get(self.model_class, record_id)
            if result:
                self.logger.debug(f"获取{self.model_class.__name__}记录成功: ID={record_id}")
            else:
                self.logger.warning(f"未找到{self.model_class.__name__}记录: ID={record_id}")
            return result
        except SQLAlchemyError as e:
            self.logger.error(f"获取{self.model_class.__name__}记录失败: ID={record_id}, 错误: {e}")
            raise
    
    async def get_all(self, session: AsyncSession, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """获取所有记录"""
        try:
            query = select(self.model_class)
            if limit:
                query = query.limit(limit).offset(offset)
            
            result = await session.execute(query)
            records = result.scalars().all()
            self.logger.debug(f"获取{self.model_class.__name__}所有记录成功: 数量={len(records)}")
            return list(records)
        except SQLAlchemyError as e:
            self.logger.error(f"获取{self.model_class.__name__}所有记录失败: {e}")
            raise
    
    async def update(self, session: AsyncSession, record_id: int, **kwargs) -> bool:
        """更新记录"""
        try:
            # 根据模型类的主键字段名进行更新
            primary_key_field = self._get_primary_key_field()
            query = update(self.model_class).where(getattr(self.model_class, primary_key_field) == record_id).values(**kwargs)
            result = await session.execute(query)
            updated = result.rowcount > 0
            
            if updated:
                self.logger.info(f"更新{self.model_class.__name__}记录成功: ID={record_id}")
            else:
                self.logger.warning(f"未找到{self.model_class.__name__}记录进行更新: ID={record_id}")
            
            return updated
        except SQLAlchemyError as e:
            self.logger.error(f"更新{self.model_class.__name__}记录失败: ID={record_id}, 错误: {e}")
            raise
    
    def _get_primary_key_field(self) -> str:
        """获取模型类的主键字段名"""
        # 根据模型类类型返回对应的主键字段名
        from module_conversation.entity.do.conversation_do import Conversation, Message, MessageContent
        
        if self.model_class == Conversation:
            return "conversation_id"
        elif self.model_class == Message:
            return "message_id"
        elif self.model_class == MessageContent:
            return "content_id"
        else:
            # 默认返回 "id"
            return "id"
    
    async def delete(self, session: AsyncSession, record_id: int) -> bool:
        """删除记录"""
        try:
            primary_key_field = self._get_primary_key_field()
            query = delete(self.model_class).where(getattr(self.model_class, primary_key_field) == record_id)
            result = await session.execute(query)
            deleted = result.rowcount > 0
            
            if deleted:
                self.logger.info(f"删除{self.model_class.__name__}记录成功: ID={record_id}")
            else:
                self.logger.warning(f"未找到{self.model_class.__name__}记录进行删除: ID={record_id}")
            
            return deleted
        except SQLAlchemyError as e:
            self.logger.error(f"删除{self.model_class.__name__}记录失败: ID={record_id}, 错误: {e}")
            raise
    
    async def count(self, session: AsyncSession, **filters) -> int:
        """统计记录数量"""
        try:
            primary_key_field = self._get_primary_key_field()
            query = select(func.count(getattr(self.model_class, primary_key_field)))
            
            # 添加过滤条件
            for field, value in filters.items():
                if hasattr(self.model_class, field) and value is not None:
                    query = query.where(getattr(self.model_class, field) == value)
            
            result = await session.execute(query)
            count = result.scalar()
            self.logger.debug(f"统计{self.model_class.__name__}记录数量: {count}")
            return count
        except SQLAlchemyError as e:
            self.logger.error(f"统计{self.model_class.__name__}记录数量失败: {e}")
            raise
    
    async def exists(self, session: AsyncSession, **filters) -> bool:
        """检查记录是否存在"""
        try:
            count = await self.count(session, **filters)
            return count > 0
        except SQLAlchemyError as e:
            self.logger.error(f"检查{self.model_class.__name__}记录存在性失败: {e}")
            raise
    
    async def bulk_create(self, session: AsyncSession, records_data: List[Dict[str, Any]]) -> List[T]:
        """批量创建记录"""
        try:
            instances = [self.model_class(**data) for data in records_data]
            session.add_all(instances)
            await session.flush()
            self.logger.info(f"批量创建{self.model_class.__name__}记录成功: 数量={len(instances)}")
            return instances
        except SQLAlchemyError as e:
            self.logger.error(f"批量创建{self.model_class.__name__}记录失败: {e}")
            raise
    
    async def bulk_update(self, session: AsyncSession, updates: List[Dict[str, Any]]) -> int:
        """批量更新记录"""
        try:
            updated_count = 0
            primary_key_field = self._get_primary_key_field()
            for update_data in updates:
                record_id = update_data.pop('id', None)
                if record_id:
                    query = update(self.model_class).where(getattr(self.model_class, primary_key_field) == record_id).values(**update_data)
                    result = await session.execute(query)
                    updated_count += result.rowcount
            
            self.logger.info(f"批量更新{self.model_class.__name__}记录成功: 数量={updated_count}")
            return updated_count
        except SQLAlchemyError as e:
            self.logger.error(f"批量更新{self.model_class.__name__}记录失败: {e}")
            raise
    
    async def bulk_delete(self, session: AsyncSession, record_ids: List[int]) -> int:
        """批量删除记录"""
        try:
            if not record_ids:
                return 0
            
            primary_key_field = self._get_primary_key_field()
            query = delete(self.model_class).where(getattr(self.model_class, primary_key_field).in_(record_ids))
            result = await session.execute(query)
            deleted_count = result.rowcount
            
            self.logger.info(f"批量删除{self.model_class.__name__}记录成功: 数量={deleted_count}")
            return deleted_count
        except SQLAlchemyError as e:
            self.logger.error(f"批量删除{self.model_class.__name__}记录失败: {e}")
            raise