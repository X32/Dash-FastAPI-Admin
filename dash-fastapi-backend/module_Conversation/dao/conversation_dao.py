from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from module_Conversation.entity.do.conversation_do import Conversation, Message, MessageContent


class ConversationDao:
    """
    会话数据访问层
    """

    @staticmethod
    async def create_conversation(db: AsyncSession, conversation: Conversation) -> Conversation:
        """
        创建会话
        
        :param db: 数据库会话
        :param conversation: 会话对象
        :return: 创建后的会话对象
        """
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def get_conversation_by_id(db: AsyncSession, conversation_id: int, user_id: int) -> Optional[Conversation]:
        """
        根据会话ID获取会话（含权限校验）
        
        :param db: 数据库会话
        :param conversation_id: 会话ID
        :param user_id: 用户ID（权限校验）
        :return: 会话对象或None
        """
        stmt = select(Conversation).where(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_conversations_by_user_id(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 20, status: int = 1) -> Tuple[List[Conversation], int]:
        """
        根据用户ID获取会话列表
        
        :param db: 数据库会话
        :param user_id: 用户ID
        :param page: 页码
        :param page_size: 每页条数
        :param status: 会话状态（1-有效/0-已删除）
        :return: 会话列表和总条数
        """
        # 计算偏移量
        offset = (page - 1) * page_size

        # 查询总条数
        total_stmt = select(func.count(Conversation.conversation_id)).where(
            Conversation.user_id == user_id,
            Conversation.status == status
        )
        total_result = await db.execute(total_stmt)
        total = total_result.scalar()

        # 查询会话列表
        stmt = select(Conversation).where(
            Conversation.user_id == user_id,
            Conversation.status == status
        ).order_by(Conversation.update_time.desc()).offset(offset).limit(page_size)
        result = await db.execute(stmt)
        conversations = result.scalars().all()

        return conversations, total

    @staticmethod
    async def update_conversation(db: AsyncSession, conversation_id: int, user_id: int, **kwargs) -> Optional[Conversation]:
        """
        更新会话信息
        
        :param db: 数据库会话
        :param conversation_id: 会话ID
        :param user_id: 用户ID（权限校验）
        :param kwargs: 更新的字段
        :return: 更新后的会话对象或None
        """
        # 先查询会话是否存在且属于当前用户
        conversation = await ConversationDao.get_conversation_by_id(db, conversation_id, user_id)
        if not conversation:
            return None

        # 更新字段
        stmt = update(Conversation).where(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == user_id
        ).values(**kwargs)
        await db.execute(stmt)
        await db.commit()
        
        # 重新查询更新后的会话
        return await ConversationDao.get_conversation_by_id(db, conversation_id, user_id)

    @staticmethod
    async def delete_conversation(db: AsyncSession, conversation_id: int, user_id: int) -> bool:
        """
        删除会话（软删除）
        
        :param db: 数据库会话
        :param conversation_id: 会话ID
        :param user_id: 用户ID（权限校验）
        :return: 是否删除成功
        """
        # 先查询会话是否存在且属于当前用户
        conversation = await ConversationDao.get_conversation_by_id(db, conversation_id, user_id)
        if not conversation:
            return False

        # 更新字段
        stmt = update(Conversation).where(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == user_id
        ).values(status=0)
        await db.execute(stmt)
        await db.commit()
        return True


class MessageDao:
    """
    消息数据访问层
    """

    @staticmethod
    async def create_message(db: AsyncSession, message: Message) -> Message:
        """
        创建消息
        
        :param db: 数据库会话
        :param message: 消息对象
        :return: 创建后的消息对象
        """
        db.add(message)
        await db.flush()
        await db.refresh(message)
        return message

    @staticmethod
    async def get_message_by_id(db: AsyncSession, message_id: int, user_id: int) -> Optional[Message]:
        """
        根据消息ID获取消息（含权限校验）
        
        :param db: 数据库会话
        :param message_id: 消息ID
        :param user_id: 用户ID（权限校验）
        :return: 消息对象或None
        """
        stmt = select(Message).join(Message.conversation).where(
            Message.message_id == message_id,
            Conversation.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_messages_by_conversation_id(db: AsyncSession, conversation_id: int, user_id: int) -> List[Message]:
        """
        根据会话ID获取消息列表（含权限校验）
        
        :param db: 数据库会话
        :param conversation_id: 会话ID
        :param user_id: 用户ID（权限校验）
        :return: 消息列表
        """
        stmt = select(Message).join(Message.conversation).where(
            Message.conversation_id == conversation_id,
            Conversation.user_id == user_id
        ).order_by(Message.seq.asc())
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def update_message(db: AsyncSession, message_id: int, user_id: int, **kwargs) -> Optional[Message]:
        """
        更新消息信息
        
        :param db: 数据库会话
        :param message_id: 消息ID
        :param user_id: 用户ID（权限校验）
        :param kwargs: 更新的字段
        :return: 更新后的消息对象或None
        """
        # 先查询消息是否存在且属于当前用户
        message = await MessageDao.get_message_by_id(db, message_id, user_id)
        if not message:
            return None

        # 更新字段
        stmt = update(Message).where(
            Message.message_id == message_id
        ).values(**kwargs).returning(Message)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_message(db: AsyncSession, message_id: int, user_id: int) -> bool:
        """
        删除消息
        
        :param db: 数据库会话
        :param message_id: 消息ID
        :param user_id: 用户ID（权限校验）
        :return: 是否删除成功
        """
        stmt = delete(Message).where(
            Message.message_id == message_id
        ).returning(Message.message_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None


class MessageContentDao:
    """
    消息内容数据访问层
    """

    @staticmethod
    async def create_message_content(db: AsyncSession, message_content: MessageContent) -> MessageContent:
        """
        创建消息内容
        
        :param db: 数据库会话
        :param message_content: 消息内容对象
        :return: 创建后的消息内容对象
        """
        db.add(message_content)
        await db.flush()
        await db.refresh(message_content)
        return message_content

    @staticmethod
    async def create_message_contents_batch(db: AsyncSession, message_contents: List[MessageContent]) -> List[MessageContent]:
        """
        批量创建消息内容
        
        :param db: 数据库会话
        :param message_contents: 消息内容对象列表
        :return: 创建后的消息内容对象列表
        """
        db.add_all(message_contents)
        await db.flush()
        return message_contents

    @staticmethod
    async def get_message_contents_by_message_id(db: AsyncSession, message_id: int, user_id: int) -> List[MessageContent]:
        """
        根据消息ID获取消息内容列表（含权限校验）
        
        :param db: 数据库会话
        :param message_id: 消息ID
        :param user_id: 用户ID（权限校验）
        :return: 消息内容列表
        """
        stmt = select(MessageContent).join(MessageContent.message).join(Message.conversation).where(
            MessageContent.message_id == message_id,
            Conversation.user_id == user_id
        ).order_by(MessageContent.seq.asc())
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def update_message_content(db: AsyncSession, content_id: int, user_id: int, **kwargs) -> Optional[MessageContent]:
        """
        更新消息内容
        
        :param db: 数据库会话
        :param content_id: 内容ID
        :param user_id: 用户ID（权限校验）
        :param kwargs: 更新的字段
        :return: 更新后的消息内容对象或None
        """
        # 先查询消息内容是否存在且属于当前用户
        stmt = select(MessageContent).join(MessageContent.message).join(Message.conversation).where(
            MessageContent.content_id == content_id,
            Conversation.user_id == user_id
        )
        result = await db.execute(stmt)
        message_content = result.scalar_one_or_none()
        if not message_content:
            return None

        # 更新字段
        stmt = update(MessageContent).where(
            MessageContent.content_id == content_id
        ).values(**kwargs).returning(MessageContent)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_message_content(db: AsyncSession, content_id: int, user_id: int) -> bool:
        """
        删除消息内容
        
        :param db: 数据库会话
        :param content_id: 内容ID
        :param user_id: 用户ID（权限校验）
        :return: 是否删除成功
        """
        stmt = delete(MessageContent).where(
            MessageContent.content_id == content_id
        ).returning(MessageContent.content_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def delete_message_contents_by_message_id(db: AsyncSession, message_id: int) -> bool:
        """
        根据消息ID删除所有消息内容
        
        :param db: 数据库会话
        :param message_id: 消息ID
        :return: 是否删除成功
        """
        stmt = delete(MessageContent).where(
            MessageContent.message_id == message_id
        )
        result = await db.execute(stmt)
        return result.rowcount > 0