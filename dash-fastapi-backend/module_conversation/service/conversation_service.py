from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from module_conversation.dao.conversation_dao import ConversationDAO, MessageDAO, MessageContentDAO
from module_conversation.entity.vo.conversation_vo import (
    ConversationVO, MessageVO, MessageContentVO, ConversationDetailVO, ConversationListVO
)
from module_conversation.entity.vo.conversation_dto import (
    CreateConversationDTO, UpdateConversationDTO, CreateMessageDTO, UpdateMessageDTO, QueryConversationDTO
)
from module_conversation.exception.conversation_exception import (
    ConversationNotFoundException, MessageNotFoundException, 
    UserPermissionException, InvalidParameterException
)


class ConversationService:
    """
    会话管理服务类
    """
    
    def __init__(self):
        self.conversation_dao = ConversationDAO()
        self.message_dao = MessageDAO()
        self.message_content_dao = MessageContentDAO()
    
    async def create_conversation(self, db: AsyncSession, user_id: int, dto: CreateConversationDTO) -> ConversationVO:
        """
        创建新会话
        """
        conversation = await self.conversation_dao.create_conversation(
            db, user_id, dto.title
        )
        
        await db.commit()
        return ConversationVO.model_validate(conversation)
    
    async def get_conversation_detail(self, db: AsyncSession, user_id: int, conversation_id: int) -> ConversationDetailVO:
        """
        获取会话详情（包含消息和内容）
        """
        # 获取会话基本信息
        conversation = await self.conversation_dao.get_conversation_by_id(
            db, conversation_id, user_id
        )
        
        if not conversation:
            raise ConversationNotFoundException(f"会话不存在或无权访问: {conversation_id}")
        
        # 获取会话的所有消息
        messages = await self.message_dao.get_messages_by_conversation(
            db, conversation_id, user_id
        )
        
        # 获取每条消息的内容
        message_vos = []
        for message in messages:
            contents = await self.message_content_dao.get_contents_by_message(
                db, message.message_id
            )
            
            content_vos = [
                MessageContentVO.model_validate(content) 
                for content in contents
            ]
            
            message_vo = MessageVO.model_validate(message)
            message_vo.contents = content_vos
            message_vos.append(message_vo)
        
        return ConversationDetailVO(
            conversation=ConversationVO.model_validate(conversation),
            messages=message_vos
        )
    
    async def update_conversation(self, db: AsyncSession, user_id: int, conversation_id: int, dto: UpdateConversationDTO) -> ConversationVO:
        """
        更新会话信息
        """
        # 检查会话是否存在且属于该用户
        conversation = await self.conversation_dao.get_conversation_by_id(
            db, conversation_id, user_id
        )
        
        if not conversation:
            raise ConversationNotFoundException(f"会话不存在或无权访问: {conversation_id}")
        
        # 更新会话信息
        update_data = dto.model_dump(exclude_unset=True)
        success = await self.conversation_dao.update_conversation(
            db, conversation_id, user_id, **update_data
        )
        
        if not success:
            raise ConversationNotFoundException(f"更新会话失败: {conversation_id}")
        
        await db.commit()
        
        # 返回更新后的会话
        updated_conversation = await self.conversation_dao.get_conversation_by_id(
            db, conversation_id, user_id
        )
        return ConversationVO.model_validate(updated_conversation)
    
    async def delete_conversation(self, db: AsyncSession, user_id: int, conversation_id: int) -> bool:
        """
        删除会话（软删除）
        """
        success = await self.conversation_dao.delete_conversation(
            db, conversation_id, user_id
        )
        
        if not success:
            raise ConversationNotFoundException(f"会话不存在或无权删除: {conversation_id}")
        
        await db.commit()
        return True
    
    async def get_conversation_list(self, db: AsyncSession, dto: QueryConversationDTO) -> ConversationListVO:
        """
        获取会话列表（分页）
        """
        conversations, total = await self.conversation_dao.get_conversations_by_user(
            db, dto.user_id, dto.status, dto.page, dto.page_size
        )
        
        conversation_vos = [
            ConversationVO.model_validate(conversation) 
            for conversation in conversations
        ]
        
        return ConversationListVO(
            total=total,
            page=dto.page,
            page_size=dto.page_size,
            conversations=conversation_vos
        )


class MessageService:
    """
    消息管理服务类
    """
    
    def __init__(self):
        self.conversation_dao = ConversationDAO()
        self.message_dao = MessageDAO()
        self.message_content_dao = MessageContentDAO()
    
    async def create_message_with_contents(
        self, 
        db: AsyncSession, 
        user_id: int, 
        conversation_id: int, 
        dto: CreateMessageDTO
    ) -> MessageVO:
        """
        创建消息及其内容（事务操作）
        """
        # 检查会话是否存在且属于该用户
        conversation = await self.conversation_dao.get_conversation_by_id(
            db, conversation_id, user_id
        )
        
        if not conversation:
            raise ConversationNotFoundException(f"会话不存在或无权访问: {conversation_id}")
        
        # 创建消息
        message = await self.message_dao.create_message(
            db, conversation_id, dto.role, dto.seq
        )
        
        # 创建消息内容（批量）
        contents_data = []
        for content_dto in dto.contents:
            content_data = {
                'message_id': message.message_id,
                'content_type': content_dto.content_type,
                'text': content_dto.text,
                'image_url': content_dto.image_url,
                'seq': content_dto.seq
            }
            contents_data.append(content_data)
        
        await self.message_content_dao.batch_create_message_contents(db, contents_data)
        
        await db.commit()
        
        # 获取完整的消息信息
        contents = await self.message_content_dao.get_contents_by_message(
            db, message.message_id
        )
        
        message_vo = MessageVO.model_validate(message)
        message_vo.contents = [
            MessageContentVO.model_validate(content) 
            for content in contents
        ]
        
        return message_vo
    
    async def update_message(
        self, 
        db: AsyncSession, 
        user_id: int, 
        message_id: int, 
        dto: UpdateMessageDTO
    ) -> MessageVO:
        """
        更新消息信息
        """
        # 获取消息并验证权限
        message = await self.message_dao.get_message_by_id(db, message_id)
        if not message:
            raise MessageNotFoundException(f"消息不存在: {message_id}")
        
        # 验证用户是否有权限修改该消息（通过会话验证）
        conversation = await self.conversation_dao.get_conversation_by_id(
            db, message.conversation_id, user_id
        )
        
        if not conversation:
            raise UserPermissionException("无权修改该消息")
        
        # 更新消息信息
        update_data = dto.model_dump(exclude_unset=True)
        success = await self.message_dao.update_message(db, message_id, **update_data)
        
        if not success:
            raise MessageNotFoundException(f"更新消息失败: {message_id}")
        
        await db.commit()
        
        # 返回更新后的消息
        updated_message = await self.message_dao.get_message_by_id(db, message_id)
        return MessageVO.model_validate(updated_message)
    
    async def delete_message(self, db: AsyncSession, user_id: int, message_id: int) -> bool:
        """
        删除消息（级联删除内容）
        """
        # 获取消息并验证权限
        message = await self.message_dao.get_message_by_id(db, message_id)
        if not message:
            raise MessageNotFoundException(f"消息不存在: {message_id}")
        
        # 验证用户是否有权限删除该消息（通过会话验证）
        conversation = await self.conversation_dao.get_conversation_by_id(
            db, message.conversation_id, user_id
        )
        
        if not conversation:
            raise UserPermissionException("无权删除该消息")
        
        # 删除消息（级联删除内容由数据库外键约束处理）
        success = await self.message_dao.delete_message(db, message_id)
        
        if not success:
            raise MessageNotFoundException(f"删除消息失败: {message_id}")
        
        await db.commit()
        return True