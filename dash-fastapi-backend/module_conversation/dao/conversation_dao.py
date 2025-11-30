from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from module_conversation.entity.do.conversation_do import Conversation, Message, MessageContent
from module_conversation.entity.vo.conversation_vo import ConversationVO, MessageVO, MessageContentVO, ConversationDetailVO
from module_conversation.entity.vo.conversation_dto import QueryConversationDTO


class ConversationDAO:
    """
    会话数据访问对象
    """
    
    @staticmethod
    async def create_conversation(db: AsyncSession, user_id: int, title: str) -> Conversation:
        """
        创建新会话
        """
        conversation = Conversation(
            user_id=user_id,
            title=title,
            status=1
        )
        db.add(conversation)
        await db.flush()
        return conversation
    
    @staticmethod
    async def get_conversation_by_id(db: AsyncSession, conversation_id: int, user_id: int, status: int = 1) -> Optional[Conversation]:
        """
        根据ID获取会话（带用户权限校验）
        """
        query = select(Conversation).where(
            and_(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == user_id,
                Conversation.status == status
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_conversation(db: AsyncSession, conversation_id: int, user_id: int, **kwargs) -> bool:
        """
        更新会话信息
        """
        query = select(Conversation).where(
            and_(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        result = await db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            return False
            
        for key, value in kwargs.items():
            if hasattr(conversation, key) and value is not None:
                setattr(conversation, key, value)
        
        return True
    
    @staticmethod
    async def delete_conversation(db: AsyncSession, conversation_id: int, user_id: int) -> bool:
        """
        删除会话（软删除，修改状态）
        """
        return await ConversationDAO.update_conversation(
            db, conversation_id, user_id, status=0
        )
    
    @staticmethod
    async def get_conversations_by_user(
        db: AsyncSession, 
        user_id: int, 
        status: int = 1, 
        page: int = 1, 
        page_size: int = 20
    ) -> tuple[List[Conversation], int]:
        """
        获取用户的会话列表（分页）
        """
        # 查询总数
        count_query = select(func.count(Conversation.conversation_id)).where(
            and_(
                Conversation.user_id == user_id,
                Conversation.status == status
            )
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 查询分页数据
        query = select(Conversation).where(
            and_(
                Conversation.user_id == user_id,
                Conversation.status == status
            )
        ).order_by(Conversation.update_time.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size)
        
        result = await db.execute(query)
        conversations = result.scalars().all()
        
        return list(conversations), total


class MessageDAO:
    """
    消息数据访问对象
    """
    
    @staticmethod
    async def create_message(db: AsyncSession, conversation_id: int, role: str, seq: int) -> Message:
        """
        创建新消息
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            seq=seq
        )
        db.add(message)
        await db.flush()
        return message
    
    @staticmethod
    async def get_message_by_id(db: AsyncSession, message_id: int) -> Optional[Message]:
        """
        根据ID获取消息
        """
        query = select(Message).where(Message.message_id == message_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_messages_by_conversation(
        db: AsyncSession, 
        conversation_id: int, 
        user_id: int
    ) -> List[Message]:
        """
        获取会话的所有消息（带用户权限校验）
        """
        query = select(Message).join(Conversation).where(
            and_(
                Message.conversation_id == conversation_id,
                Conversation.user_id == user_id
            )
        ).order_by(Message.seq.asc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_message(db: AsyncSession, message_id: int, **kwargs) -> bool:
        """
        更新消息信息
        """
        query = select(Message).where(Message.message_id == message_id)
        result = await db.execute(query)
        message = result.scalar_one_or_none()
        
        if not message:
            return False
            
        for key, value in kwargs.items():
            if hasattr(message, key) and value is not None:
                setattr(message, key, value)
        
        return True
    
    @staticmethod
    async def delete_message(db: AsyncSession, message_id: int) -> bool:
        """
        删除消息（级联删除内容）
        """
        query = select(Message).where(Message.message_id == message_id)
        result = await db.execute(query)
        message = result.scalar_one_or_none()
        
        if not message:
            return False
            
        await db.delete(message)
        return True


class MessageContentDAO:
    """
    消息内容数据访问对象
    """
    
    @staticmethod
    async def create_message_content(
        db: AsyncSession, 
        message_id: int, 
        content_type: str, 
        seq: int,
        text: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> MessageContent:
        """
        创建消息内容
        """
        content = MessageContent(
            message_id=message_id,
            content_type=content_type,
            text=text,
            image_url=image_url,
            seq=seq
        )
        db.add(content)
        await db.flush()
        return content
    
    @staticmethod
    async def get_contents_by_message(db: AsyncSession, message_id: int) -> List[MessageContent]:
        """
        获取消息的所有内容
        """
        query = select(MessageContent).where(
            MessageContent.message_id == message_id
        ).order_by(MessageContent.seq.asc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_message_content(
        db: AsyncSession, 
        content_id: int, 
        **kwargs
    ) -> bool:
        """
        更新消息内容
        """
        query = select(MessageContent).where(MessageContent.content_id == content_id)
        result = await db.execute(query)
        content = result.scalar_one_or_none()
        
        if not content:
            return False
            
        for key, value in kwargs.items():
            if hasattr(content, key) and value is not None:
                setattr(content, key, value)
        
        return True
    
    @staticmethod
    async def delete_message_content(db: AsyncSession, content_id: int) -> bool:
        """
        删除消息内容
        """
        query = select(MessageContent).where(MessageContent.content_id == content_id)
        result = await db.execute(query)
        content = result.scalar_one_or_none()
        
        if not content:
            return False
            
        await db.delete(content)
        return True
    
    @staticmethod
    async def batch_create_message_contents(
        db: AsyncSession, 
        contents: List[dict]
    ) -> List[MessageContent]:
        """
        批量创建消息内容
        """
        message_contents = []
        for content_data in contents:
            content = MessageContent(**content_data)
            db.add(content)
            message_contents.append(content)
        
        await db.flush()
        return message_contents