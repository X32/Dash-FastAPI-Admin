import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from module_conversation.service.conversation_service import ConversationService, MessageService
from module_conversation.entity.vo.conversation_dto import CreateConversationDTO, UpdateConversationDTO, CreateMessageDTO, CreateMessageContentDTO
from module_conversation.entity.vo.conversation_vo import ConversationVO, MessageVO
from module_conversation.exception.conversation_exception import (
    ConversationNotFoundException, MessageNotFoundException, 
    UserPermissionException, InvalidParameterException
)


class TestConversationService:
    """会话服务测试类"""
    
    @pytest.fixture
    def conversation_service(self):
        return ConversationService()
    
    @pytest.fixture
    def mock_db_session(self):
        """创建模拟数据库会话"""
        session = AsyncMock(spec=AsyncSession)
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        return session
    
    @pytest.mark.asyncio
    async def test_create_conversation_success(self, conversation_service, mock_db_session):
        """测试成功创建会话"""
        # 模拟DAO方法
        conversation_service.conversation_dao.create_conversation = AsyncMock()
        conversation_service.conversation_dao.create_conversation.return_value = MagicMock(
            conversation_id=1,
            user_id=1,
            title="测试会话",
            status=1
        )
        
        # 创建DTO
        dto = CreateConversationDTO(title="测试会话")
        
        # 调用服务
        result = await conversation_service.create_conversation(mock_db_session, 1, dto)
        
        # 验证结果
        assert isinstance(result, ConversationVO)
        assert result.conversation_id == 1
        assert result.title == "测试会话"
        
        # 验证commit被调用
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_conversation_detail_success(self, conversation_service, mock_db_session):
        """测试成功获取会话详情"""
        # 模拟会话
        mock_conversation = MagicMock(
            conversation_id=1,
            user_id=1,
            title="测试会话",
            status=1
        )
        
        # 模拟消息
        mock_message = MagicMock(
            message_id=1,
            conversation_id=1,
            role="user",
            seq=1
        )
        
        # 模拟消息内容
        mock_content = MagicMock(
            content_id=1,
            message_id=1,
            content_type="text",
            text="测试内容"
        )
        
        # 设置DAO模拟
        conversation_service.conversation_dao.get_conversation_by_id = AsyncMock()
        conversation_service.conversation_dao.get_conversation_by_id.return_value = mock_conversation
        
        conversation_service.message_dao.get_messages_by_conversation = AsyncMock()
        conversation_service.message_dao.get_messages_by_conversation.return_value = [mock_message]
        
        conversation_service.message_content_dao.get_contents_by_message = AsyncMock()
        conversation_service.message_content_dao.get_contents_by_message.return_value = [mock_content]
        
        # 调用服务
        result = await conversation_service.get_conversation_detail(mock_db_session, 1, 1)
        
        # 验证结果
        assert result.conversation.conversation_id == 1
        assert len(result.messages) == 1
        assert len(result.messages[0].contents) == 1
        assert result.messages[0].contents[0].text == "测试内容"
    
    @pytest.mark.asyncio
    async def test_get_conversation_detail_not_found(self, conversation_service, mock_db_session):
        """测试会话不存在异常"""
        # 设置DAO返回None
        conversation_service.conversation_dao.get_conversation_by_id = AsyncMock()
        conversation_service.conversation_dao.get_conversation_by_id.return_value = None
        
        # 验证抛出异常
        with pytest.raises(ConversationNotFoundException):
            await conversation_service.get_conversation_detail(mock_db_session, 1, 999)
    
    @pytest.mark.asyncio
    async def test_update_conversation_success(self, conversation_service, mock_db_session):
        """测试成功更新会话"""
        # 模拟原始会话
        mock_conversation = MagicMock(
            conversation_id=1,
            user_id=1,
            title="原始标题",
            status=1
        )
        
        # 模拟更新后的会话
        mock_updated_conversation = MagicMock(
            conversation_id=1,
            user_id=1,
            title="新标题",
            status=1
        )
        
        # 设置DAO模拟
        conversation_service.conversation_dao.get_conversation_by_id = AsyncMock()
        conversation_service.conversation_dao.get_conversation_by_id.return_value = mock_conversation
        
        conversation_service.conversation_dao.update_conversation = AsyncMock()
        conversation_service.conversation_dao.update_conversation.return_value = True
        
        conversation_service.conversation_dao.get_conversation_by_id = AsyncMock()
        conversation_service.conversation_dao.get_conversation_by_id.return_value = mock_updated_conversation
        
        # 创建DTO
        dto = UpdateConversationDTO(title="新标题")
        
        # 调用服务
        result = await conversation_service.update_conversation(mock_db_session, 1, 1, dto)
        
        # 验证结果
        assert result.title == "新标题"
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_conversation_permission_denied(self, conversation_service, mock_db_session):
        """测试更新会话权限被拒绝"""
        # 设置DAO返回None（表示会话不存在或无权访问）
        conversation_service.conversation_dao.get_conversation_by_id = AsyncMock()
        conversation_service.conversation_dao.get_conversation_by_id.return_value = None
        
        # 创建DTO
        dto = UpdateConversationDTO(title="新标题")
        
        # 验证抛出异常
        with pytest.raises(ConversationNotFoundException):
            await conversation_service.update_conversation(mock_db_session, 2, 1, dto)
    
    @pytest.mark.asyncio
    async def test_delete_conversation_success(self, conversation_service, mock_db_session):
        """测试成功删除会话"""
        # 设置DAO模拟
        conversation_service.conversation_dao.delete_conversation = AsyncMock()
        conversation_service.conversation_dao.delete_conversation.return_value = True
        
        # 调用服务
        result = await conversation_service.delete_conversation(mock_db_session, 1, 1)
        
        # 验证结果
        assert result is True
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_conversation_list_success(self, conversation_service, mock_db_session):
        """测试成功获取会话列表"""
        # 模拟会话数据
        mock_conversations = [
            MagicMock(conversation_id=1, user_id=1, title="会话1", status=1),
            MagicMock(conversation_id=2, user_id=1, title="会话2", status=1)
        ]
        
        # 设置DAO模拟
        conversation_service.conversation_dao.get_conversations_by_user = AsyncMock()
        conversation_service.conversation_dao.get_conversations_by_user.return_value = (mock_conversations, 2)
        
        # 创建查询DTO
        from module_conversation.entity.vo.conversation_dto import QueryConversationDTO
        dto = QueryConversationDTO(user_id=1, status=1, page=1, page_size=10)
        
        # 调用服务
        result = await conversation_service.get_conversation_list(mock_db_session, dto)
        
        # 验证结果
        assert result.total == 2
        assert result.page == 1
        assert result.page_size == 10
        assert len(result.conversations) == 2


class TestMessageService:
    """消息服务测试类"""
    
    @pytest.fixture
    def message_service(self):
        return MessageService()
    
    @pytest.fixture
    def mock_db_session(self):
        """创建模拟数据库会话"""
        session = AsyncMock(spec=AsyncSession)
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        return session
    
    @pytest.mark.asyncio
    async def test_create_message_with_contents_success(self, message_service, mock_db_session):
        """测试成功创建消息及其内容"""
        # 模拟会话
        mock_conversation = MagicMock(
            conversation_id=1,
            user_id=1,
            title="测试会话",
            status=1
        )
        
        # 模拟消息
        mock_message = MagicMock(
            message_id=1,
            conversation_id=1,
            role="user",
            seq=1
        )
        
        # 模拟消息内容
        mock_content = MagicMock(
            content_id=1,
            message_id=1,
            content_type="text",
            text="测试内容"
        )
        
        # 设置DAO模拟
        message_service.conversation_dao.get_conversation_by_id = AsyncMock()
        message_service.conversation_dao.get_conversation_by_id.return_value = mock_conversation
        
        message_service.message_dao.create_message = AsyncMock()
        message_service.message_dao.create_message.return_value = mock_message
        
        message_service.message_content_dao.batch_create_message_contents = AsyncMock()
        
        message_service.message_content_dao.get_contents_by_message = AsyncMock()
        message_service.message_content_dao.get_contents_by_message.return_value = [mock_content]
        
        # 创建DTO
        content_dto = CreateMessageContentDTO(content_type="text", text="测试内容", seq=1)
        dto = CreateMessageDTO(role="user", seq=1, contents=[content_dto])
        
        # 调用服务
        result = await message_service.create_message_with_contents(mock_db_session, 1, 1, dto)
        
        # 验证结果
        assert isinstance(result, MessageVO)
        assert result.message_id == 1
        assert result.role == "user"
        assert len(result.contents) == 1
        assert result.contents[0].text == "测试内容"
        
        # 验证commit被调用
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_message_conversation_not_found(self, message_service, mock_db_session):
        """测试创建消息时会话不存在"""
        # 设置DAO返回None
        message_service.conversation_dao.get_conversation_by_id = AsyncMock()
        message_service.conversation_dao.get_conversation_by_id.return_value = None
        
        # 创建DTO
        content_dto = CreateMessageContentDTO(content_type="text", text="测试内容", seq=1)
        dto = CreateMessageDTO(role="user", seq=1, contents=[content_dto])
        
        # 验证抛出异常
        with pytest.raises(ConversationNotFoundException):
            await message_service.create_message_with_contents(mock_db_session, 1, 999, dto)
    
    @pytest.mark.asyncio
    async def test_update_message_success(self, message_service, mock_db_session):
        """测试成功更新消息"""
        # 模拟消息
        mock_message = MagicMock(
            message_id=1,
            conversation_id=1,
            role="user",
            seq=1
        )
        
        # 模拟会话
        mock_conversation = MagicMock(
            conversation_id=1,
            user_id=1,
            title="测试会话",
            status=1
        )
        
        # 模拟更新后的消息
        mock_updated_message = MagicMock(
            message_id=1,
            conversation_id=1,
            role="assistant",
            seq=2
        )
        
        # 设置DAO模拟
        message_service.message_dao.get_message_by_id = AsyncMock()
        message_service.message_dao.get_message_by_id.return_value = mock_message
        
        message_service.conversation_dao.get_conversation_by_id = AsyncMock()
        message_service.conversation_dao.get_conversation_by_id.return_value = mock_conversation
        
        message_service.message_dao.update_message = AsyncMock()
        message_service.message_dao.update_message.return_value = True
        
        message_service.message_dao.get_message_by_id = AsyncMock()
        message_service.message_dao.get_message_by_id.return_value = mock_updated_message
        
        # 创建DTO
        dto = UpdateMessageDTO(role="assistant", seq=2)
        
        # 调用服务
        result = await message_service.update_message(mock_db_session, 1, 1, dto)
        
        # 验证结果
        assert result.role == "assistant"
        assert result.seq == 2
        mock_db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_message_permission_denied(self, message_service, mock_db_session):
        """测试更新消息权限被拒绝"""
        # 模拟消息
        mock_message = MagicMock(
            message_id=1,
            conversation_id=1,
            role="user",
            seq=1
        )
        
        # 设置DAO模拟
        message_service.message_dao.get_message_by_id = AsyncMock()
        message_service.message_dao.get_message_by_id.return_value = mock_message
        
        # 会话验证返回None（表示无权访问）
        message_service.conversation_dao.get_conversation_by_id = AsyncMock()
        message_service.conversation_dao.get_conversation_by_id.return_value = None
        
        # 创建DTO
        dto = UpdateMessageDTO(role="assistant", seq=2)
        
        # 验证抛出异常
        with pytest.raises(UserPermissionException):
            await message_service.update_message(mock_db_session, 2, 1, dto)
    
    @pytest.mark.asyncio
    async def test_delete_message_success(self, message_service, mock_db_session):
        """测试成功删除消息"""
        # 模拟消息
        mock_message = MagicMock(
            message_id=1,
            conversation_id=1,
            role="user",
            seq=1
        )
        
        # 模拟会话
        mock_conversation = MagicMock(
            conversation_id=1,
            user_id=1,
            title="测试会话",
            status=1
        )
        
        # 设置DAO模拟
        message_service.message_dao.get_message_by_id = AsyncMock()
        message_service.message_dao.get_message_by_id.return_value = mock_message
        
        message_service.conversation_dao.get_conversation_by_id = AsyncMock()
        message_service.conversation_dao.get_conversation_by_id.return_value = mock_conversation
        
        message_service.message_dao.delete_message = AsyncMock()
        message_service.message_dao.delete_message.return_value = True
        
        # 调用服务
        result = await message_service.delete_message(mock_db_session, 1, 1)
        
        # 验证结果
        assert result is True
        mock_db_session.commit.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])