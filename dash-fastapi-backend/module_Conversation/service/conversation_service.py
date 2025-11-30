from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from module_Conversation.entity.do.conversation_do import Conversation, Message, MessageContent
from module_Conversation.dao.conversation_dao import ConversationDao, MessageDao, MessageContentDao


class ConversationService:
    """
    会话业务逻辑层
    """

    @staticmethod
    async def create_conversation(db: AsyncSession, user_id: int, title: str, remark: Optional[str] = None) -> Conversation:
        """
        创建会话
        
        :param db: 数据库会话
        :param user_id: 用户ID
        :param title: 会话标题
        :param remark: 备注
        :return: 创建后的会话对象
        """
        conversation = Conversation(
            user_id=user_id,
            title=title,
            remark=remark
        )
        return await ConversationDao.create_conversation(db, conversation)

    @staticmethod
    async def get_conversation_detail(db: AsyncSession, conversation_id: int, user_id: int) -> Optional[Conversation]:
        """
        获取会话详情（含消息和消息内容）
        
        :param db: 数据库会话
        :param conversation_id: 会话ID
        :param user_id: 用户ID（权限校验）
        :return: 会话对象或None
        """
        conversation = await ConversationDao.get_conversation_by_id(db, conversation_id, user_id)
        if conversation:
            # 预加载消息和消息内容
            await conversation.awaitable_attrs.messages
            for message in conversation.messages:
                await message.awaitable_attrs.message_contents
        return conversation

    @staticmethod
    async def get_conversation_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 20, status: int = 1) -> Tuple[List[Conversation], int]:
        """
        获取会话列表
        
        :param db: 数据库会话
        :param user_id: 用户ID
        :param page: 页码
        :param page_size: 每页条数
        :param status: 会话状态（1-有效/0-已删除）
        :return: 会话列表和总条数
        """
        return await ConversationDao.get_conversations_by_user_id(db, user_id, page, page_size, status)

    @staticmethod
    async def update_conversation(db: AsyncSession, conversation_id: int, user_id: int, title: Optional[str] = None, remark: Optional[str] = None) -> Optional[Conversation]:
        """
        更新会话信息
        
        :param db: 数据库会话
        :param conversation_id: 会话ID
        :param user_id: 用户ID（权限校验）
        :param title: 会话标题
        :param remark: 备注
        :return: 更新后的会话对象或None
        """
        kwargs = {}
        if title is not None:
            kwargs['title'] = title
        if remark is not None:
            kwargs['remark'] = remark
        kwargs['update_time'] = datetime.now()

        return await ConversationDao.update_conversation(db, conversation_id, user_id, **kwargs)

    @staticmethod
    async def delete_conversation(db: AsyncSession, conversation_id: int, user_id: int) -> bool:
        """
        删除会话（软删除）
        
        :param db: 数据库会话
        :param conversation_id: 会话ID
        :param user_id: 用户ID（权限校验）
        :return: 是否删除成功
        """
        return await ConversationDao.delete_conversation(db, conversation_id, user_id)


class MessageService:
    """
    消息业务逻辑层
    """

    @staticmethod
    async def create_message(db: AsyncSession, conversation_id: int, user_id: int, role: str, contents: List[dict]) -> Message:
        """
        创建消息（含内容）
        
        :param db: 数据库会话
        :param conversation_id: 会话ID
        :param user_id: 用户ID（权限校验）
        :param role: 角色
        :param contents: 消息内容列表
        :return: 创建后的消息对象
        """
        # 先校验会话是否存在且属于当前用户
        conversation = await ConversationDao.get_conversation_by_id(db, conversation_id, user_id)
        if not conversation:
            return None

        # 获取当前会话的最大消息序列
        messages = await MessageDao.get_messages_by_conversation_id(db, conversation_id, user_id)
        max_seq = max((message.seq for message in messages), default=0)

        # 创建消息
        message = Message(
            conversation_id=conversation_id,
            role=role,
            seq=max_seq + 1
        )
        message = await MessageDao.create_message(db, message)

        # 创建消息内容
        message_contents = []
        for i, content in enumerate(contents):
            content_type = content.get('content_type')
            if content_type not in ['text', 'image_url']:
                continue

            message_content = MessageContent(
                message_id=message.message_id,
                content_type=content_type,
                text=content.get('text'),
                image_url=content.get('image_url'),
                seq=i + 1
            )
            message_contents.append(message_content)

        if message_contents:
            await MessageContentDao.create_message_contents_batch(db, message_contents)

        # 更新会话的更新时间
        await ConversationDao.update_conversation(db, conversation_id, user_id, update_time=datetime.now())

        return message

    @staticmethod
    async def get_message_detail(db: AsyncSession, message_id: int, user_id: int) -> Optional[Message]:
        """
        获取消息详情（含内容）
        
        :param db: 数据库会话
        :param message_id: 消息ID
        :param user_id: 用户ID（权限校验）
        :return: 消息对象或None
        """
        message = await MessageDao.get_message_by_id(db, message_id, user_id)
        if message:
            # 预加载消息内容
            await message.awaitable_attrs.message_contents
        return message

    @staticmethod
    async def update_message(db: AsyncSession, message_id: int, user_id: int, role: Optional[str] = None, contents: Optional[List[dict]] = None) -> Optional[Message]:
        """
        更新消息信息
        
        :param db: 数据库会话
        :param message_id: 消息ID
        :param user_id: 用户ID（权限校验）
        :param role: 角色
        :param contents: 消息内容列表
        :return: 更新后的消息对象或None
        """
        kwargs = {}
        if role is not None:
            kwargs['role'] = role
        kwargs['update_time'] = datetime.now()

        message = await MessageDao.update_message(db, message_id, user_id, **kwargs)
        if message and contents:
            # 删除原有消息内容
            await MessageContentDao.delete_message_contents_by_message_id(db, message_id)
            # 创建新的消息内容
            message_contents = []
            for i, content in enumerate(contents):
                content_type = content.get('content_type')
                if content_type not in ['text', 'image_url']:
                    continue

                message_content = MessageContent(
                    message_id=message.message_id,
                    content_type=content_type,
                    text=content.get('text'),
                    image_url=content.get('image_url'),
                    seq=i + 1
                )
                message_contents.append(message_content)

            if message_contents:
                await MessageContentDao.create_message_contents_batch(db, message_contents)

            # 更新会话的更新时间
            await ConversationDao.update_conversation(db, message.conversation_id, user_id, update_time=datetime.now())

        return message

    @staticmethod
    async def delete_message(db: AsyncSession, message_id: int, user_id: int) -> bool:
        """
        删除消息
        
        :param db: 数据库会话
        :param message_id: 消息ID
        :param user_id: 用户ID（权限校验）
        :return: 是否删除成功
        """
        # 先查询消息是否存在且属于当前用户
        message = await MessageDao.get_message_by_id(db, message_id, user_id)
        if not message:
            return False

        # 删除消息（会级联删除消息内容）
        success = await MessageDao.delete_message(db, message_id, user_id)
        if success:
            # 更新会话的更新时间
            await ConversationDao.update_conversation(db, message.conversation_id, user_id, update_time=datetime.now())

        return success