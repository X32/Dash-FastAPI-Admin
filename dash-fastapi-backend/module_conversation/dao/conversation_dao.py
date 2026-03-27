#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话管理模块数据访问层
集成连接池管理和性能优化功能
"""

from typing import Optional, List, Dict, Tuple
from sqlalchemy import select, update, delete, desc, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from module_conversation.entity.do.conversation_do import Conversation
from module_conversation.entity.do.conversation_do import Message
from module_conversation.entity.do.conversation_do import MessageContent
from module_conversation.dao.base_dao import BaseConversationDAO
from utils.log_util import logger


class ConversationDAO(BaseConversationDAO[Conversation]):
    """会话数据访问对象 - 集成连接池管理"""
    
    def __init__(self):
        super().__init__(Conversation)

    async def create_conversation(self, session: AsyncSession, title: str, user_id: int) -> Conversation:
        """创建会话"""
        conversation = self.model_class(title=title, user_id=user_id)
        session.add(conversation)
        await session.flush()
        await session.refresh(conversation)
        self.logger.info(f"创建会话成功: 用户ID={user_id}, 标题={title}")
        return conversation

    async def get_conversation_by_id(self, session: AsyncSession, conversation_id: int) -> Optional[Conversation]:
        """根据ID获取会话"""
        return await self.get_by_id(session, conversation_id)

    async def get_conversations_by_user(self, session: AsyncSession, user_id: int, status: Optional[int] = None, page: int = 1, page_size: int = 20) -> Tuple[List[Conversation], int]:
        """获取用户的会话列表（支持分页和状态筛选）"""
        try:
            # 基础查询
            base_query = select(Conversation).where(Conversation.user_id == user_id)
            
            # 如果有状态筛选
            if status is not None:
                base_query = base_query.where(Conversation.status == status)
            
            # 计算总数
            count_query = select(func.count()).select_from(base_query.subquery())
            count_result = await session.execute(count_query)
            total = count_result.scalar() or 0
            
            # 分页查询
            offset = (page - 1) * page_size
            paginated_query = base_query.order_by(desc(Conversation.create_time)).limit(page_size).offset(offset)
            
            result = await session.execute(paginated_query)
            conversations = result.scalars().all()
            self.logger.info(f"获取用户会话列表成功: 用户ID={user_id}, 数量={len(conversations)}, 总数={total}")
            
            # 返回会话列表和总数
            return list(conversations), total
        except SQLAlchemyError as e:
            self.logger.error(f"获取用户会话列表失败: 用户ID={user_id}, 错误: {e}")
            raise

    async def update_conversation(self, session: AsyncSession, conversation_id: int, **kwargs) -> bool:
        """更新会话信息"""
        return await self.update(session, conversation_id, **kwargs)

    async def delete_conversation(self, session: AsyncSession, conversation_id: int) -> bool:
        """删除会话"""
        return await self.delete(session, conversation_id)

    async def get_conversation_count(self, session: AsyncSession, user_id: Optional[int] = None) -> int:
        """获取会话数量"""
        if user_id:
            return await self.count(session, user_id=user_id)
        return await self.count(session)


class MessageDAO(BaseConversationDAO[Message]):
    """消息数据访问对象 - 集成连接池管理"""
    
    def __init__(self):
        super().__init__(Message)

    async def create_message(self, session: AsyncSession, conversation_id: int, role: str, seq: int) -> Message:
        """创建新消息"""
        return await self.create(session, conversation_id=conversation_id, role=role, seq=seq)

    async def get_message_by_id(self, session: AsyncSession, message_id: int) -> Optional[Message]:
        """根据ID获取消息"""
        return await self.get_by_id(session, message_id)

    async def get_messages_by_conversation(
        self,
        session: AsyncSession,
        conversation_id: int,
        user_id: int
    ) -> List[Message]:
        """获取会话的所有消息（带用户权限校验）"""
        try:
            query = select(Message).join(Conversation).where(
                and_(
                    Message.conversation_id == conversation_id,
                    Conversation.user_id == user_id
                )
            ).order_by(Message.seq.asc())
            
            result = await session.execute(query)
            messages = result.scalars().all()
            self.logger.info(f"获取用户会话消息列表成功: 用户ID={user_id}, 会话ID={conversation_id}, 数量={len(messages)}")
            return list(messages)
        except SQLAlchemyError as e:
            self.logger.error(f"获取用户会话消息列表失败: 用户ID={user_id}, 会话ID={conversation_id}, 错误: {e}")
            raise

    async def update_message(self, session: AsyncSession, message_id: int, **kwargs) -> bool:
        """更新消息信息"""
        return await self.update(session, message_id, **kwargs)

    async def delete_message(self, session: AsyncSession, message_id: int) -> bool:
        """删除消息"""
        return await self.delete(session, message_id)


class MessageContentDAO(BaseConversationDAO[MessageContent]):
    """消息内容数据访问对象 - 集成连接池管理"""
    
    def __init__(self):
        super().__init__(MessageContent)

    async def create_content(self, session: AsyncSession, message_id: int, content_type: str, content_data: str) -> MessageContent:
        """创建消息内容"""
        return await self.create(session, message_id=message_id, content_type=content_type, content_data=content_data)

    async def get_content_by_id(self, session: AsyncSession, content_id: int) -> Optional[MessageContent]:
        """根据ID获取消息内容"""
        return await self.get_by_id(session, content_id)

    async def get_contents_by_message(self, session: AsyncSession, message_id: int) -> List[MessageContent]:
        """获取消息的所有内容"""
        try:
            query = select(MessageContent).where(MessageContent.message_id == message_id).order_by(MessageContent.create_time)
            result = await session.execute(query)
            contents = result.scalars().all()
            self.logger.info(f"获取消息内容列表成功: 消息ID={message_id}, 数量={len(contents)}")
            return list(contents)
        except SQLAlchemyError as e:
            self.logger.error(f"获取消息内容列表失败: 消息ID={message_id}, 错误: {e}")
            raise

    async def update_content(self, session: AsyncSession, content_id: int, **kwargs) -> bool:
        """更新消息内容"""
        return await self.update(session, content_id, **kwargs)

    async def delete_content(self, session: AsyncSession, content_id: int) -> bool:
        """删除消息内容"""
        return await self.delete(session, content_id)

    async def bulk_create_contents(self, session: AsyncSession, contents_data: List[Dict]) -> List[MessageContent]:
        """批量创建消息内容"""
        return await self.bulk_create(session, contents_data)

    async def bulk_delete_contents(self, session: AsyncSession, content_ids: List[int]) -> int:
        """批量删除消息内容"""
        return await self.bulk_delete(session, content_ids)