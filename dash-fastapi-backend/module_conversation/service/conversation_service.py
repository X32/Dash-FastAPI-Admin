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
        # 创建会话对象
        from module_conversation.entity.do.conversation_do import Conversation
        from datetime import datetime
        
        conversation = Conversation(
            user_id=user_id,
            title=dto.title,
            status=1,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        
        db.add(conversation)
        await db.flush()
        
        # 获取创建后的ID和时间戳
        conversation_id = conversation.conversation_id
        create_time = conversation.create_time
        update_time = conversation.update_time
        
        # 提交事务
        await db.commit()
        
        # 返回VO对象
        return ConversationVO(
            conversation_id=conversation_id,
            user_id=user_id,
            title=dto.title,
            status=1,
            create_time=create_time,
            update_time=update_time
        )
    
    async def get_conversation_detail(self, db: AsyncSession, user_id: int, conversation_id: int) -> ConversationDetailVO:
        """
        获取会话详情（包含消息和内容）
        """
        # 获取会话基本信息
        conversation = await self.conversation_dao.get_conversation_by_id(
            db, conversation_id
        )
        
        if not conversation:
            raise ConversationNotFoundException(f"会话不存在: {conversation_id}")
        
        # 验证用户权限
        if conversation.user_id != user_id:
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
            
            # 在事务提交前获取所有需要的数据
            message_vo = MessageVO(
                message_id=message.message_id,
                conversation_id=message.conversation_id,
                role=message.role,
                seq=message.seq,
                create_time=message.create_time,
                contents=content_vos
            )
            message_vos.append(message_vo)
        
        # 在事务提交前获取所有需要的数据
        conversation_vo = ConversationVO(
            conversation_id=conversation.conversation_id,
            user_id=conversation.user_id,
            title=conversation.title,
            status=conversation.status,
            create_time=conversation.create_time,
            update_time=conversation.update_time
        )
        
        return ConversationDetailVO(
            conversation=conversation_vo,
            messages=message_vos
        )
    
    async def update_conversation(self, db: AsyncSession, user_id: int, conversation_id: int, dto: UpdateConversationDTO) -> ConversationVO:
        """
        更新会话信息
        """
        # 检查会话是否存在且属于该用户
        conversation = await self.conversation_dao.get_conversation_by_id(
            db, conversation_id
        )
        
        if not conversation:
            raise ConversationNotFoundException(f"会话不存在: {conversation_id}")
        
        # 验证用户权限
        if conversation.user_id != user_id:
            raise ConversationNotFoundException(f"会话不存在或无权访问: {conversation_id}")
        
        # 更新会话信息
        update_data = dto.model_dump(exclude_unset=True)
        success = await self.conversation_dao.update_conversation(
            db, conversation_id, **update_data
        )
        
        if not success:
            raise ConversationNotFoundException(f"更新会话失败: {conversation_id}")
        
        await db.commit()
        
        # 获取更新后的会话信息（在事务提交前）
        updated_conversation = await self.conversation_dao.get_conversation_by_id(
            db, conversation_id
        )
        
        await db.commit()
        
        # 返回构建好的VO对象
        return ConversationVO(
            conversation_id=updated_conversation.conversation_id,
            user_id=updated_conversation.user_id,
            title=updated_conversation.title,
            status=updated_conversation.status,
            create_time=updated_conversation.create_time,
            update_time=updated_conversation.update_time
        )
    
    async def delete_conversation(self, db: AsyncSession, user_id: int, conversation_id: int) -> bool:
        """
        删除会话（软删除）
        """
        # 检查会话是否存在且属于该用户
        conversation = await self.conversation_dao.get_conversation_by_id(
            db, conversation_id
        )
        
        if not conversation:
            raise ConversationNotFoundException(f"会话不存在: {conversation_id}")
        
        # 验证用户权限
        if conversation.user_id != user_id:
            raise ConversationNotFoundException(f"会话不存在或无权删除: {conversation_id}")
        
        success = await self.conversation_dao.delete_conversation(
            db, conversation_id
        )
        
        if not success:
            raise ConversationNotFoundException(f"删除会话失败: {conversation_id}")
        
        await db.commit()
        return True
    
    async def get_conversation_list(self, db: AsyncSession, dto: QueryConversationDTO) -> ConversationListVO:
        """
        获取会话列表（分页）
        """
        conversations, total = await self.conversation_dao.get_conversations_by_user(
            db, dto.user_id, dto.status, dto.page, dto.page_size
        )
        
        # 在事务提交前构建VO对象
        conversation_vos = []
        for conversation in conversations:
            conversation_vos.append(ConversationVO(
                conversation_id=conversation.conversation_id,
                user_id=conversation.user_id,
                title=conversation.title,
                status=conversation.status,
                create_time=conversation.create_time,
                update_time=conversation.update_time
            ))
        
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
            db, conversation_id
        )
        
        if not conversation:
            raise ConversationNotFoundException(f"会话不存在: {conversation_id}")
        
        # 验证用户权限
        if conversation.user_id != user_id:
            raise ConversationNotFoundException(f"会话不存在或无权访问: {conversation_id}")
        
        # 创建消息
        message = await self.message_dao.create_message(
            db, conversation_id, dto.role, dto.seq
        )
        
        # 保存所有需要的属性，避免事务提交后访问对象属性
        message_id = message.message_id
        create_time = message.create_time
        
        # 创建消息内容（批量）
        contents_data = []
        for content_dto in dto.contents:
            content_data = {
                'message_id': message_id,
                'content_type': content_dto.content_type,
                'text': content_dto.text,
                'image_url': content_dto.image_url,
                'seq': content_dto.seq
            }
            contents_data.append(content_data)
        
        await self.message_content_dao.bulk_create_contents(db, contents_data)
        
        # 获取完整的消息信息（在事务提交前）
        contents = await self.message_content_dao.get_contents_by_message(
            db, message_id
        )
        
        # 将内容转换为VO对象（在事务提交前）
        content_vos = [
            MessageContentVO.model_validate(content) 
            for content in contents
        ]
        
        await db.commit()
        
        # 构建响应对象
        message_vo = MessageVO(
            message_id=message_id,
            conversation_id=conversation_id,
            role=dto.role,
            seq=dto.seq,
            create_time=create_time,
            contents=content_vos
        )
        
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
            db, message.conversation_id
        )
        
        if not conversation:
            raise ConversationNotFoundException(f"会话不存在: {message.conversation_id}")
        
        if conversation.user_id != user_id:
            raise UserPermissionException("无权修改该消息")
        
        # 更新消息信息
        update_data = dto.model_dump(exclude_unset=True)
        success = await self.message_dao.update_message(db, message_id, **update_data)
        
        if not success:
            raise MessageNotFoundException(f"更新消息失败: {message_id}")
        
        # 获取更新后的消息和关联内容（在事务提交前）
        updated_message = await self.message_dao.get_message_by_id(db, message_id)
        contents = await self.message_content_dao.get_contents_by_message(db, message_id)
        
        # 在事务提交前保存所有需要的属性
        message_id_val = updated_message.message_id
        conversation_id_val = updated_message.conversation_id
        role_val = updated_message.role
        seq_val = updated_message.seq
        create_time_val = updated_message.create_time
        
        # 构建内容VO对象（在事务提交前）
        content_vos = [
            MessageContentVO.model_validate(content) 
            for content in contents
        ]
        
        await db.commit()
        
        # 返回构建好的VO对象
        return MessageVO(
            message_id=message_id_val,
            conversation_id=conversation_id_val,
            role=role_val,
            seq=seq_val,
            create_time=create_time_val,
            contents=content_vos
        )
    
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
            db, message.conversation_id
        )
        
        if not conversation:
            raise ConversationNotFoundException(f"会话不存在: {message.conversation_id}")
        
        if conversation.user_id != user_id:
            raise UserPermissionException("无权删除该消息")
        
        # 删除消息（级联删除内容由数据库外键约束处理）
        success = await self.message_dao.delete_message(db, message_id)
        
        if not success:
            raise MessageNotFoundException(f"删除消息失败: {message_id}")
        
        await db.commit()
        return True