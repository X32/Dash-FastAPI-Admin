import pytest
import pytest_asyncio
import asyncio
from typing import List
from module_conversation.dao.conversation_dao import ConversationDAO, MessageDAO, MessageContentDAO
from module_conversation.entity.do.conversation_do import Conversation, Message, MessageContent
from module_conversation.entity.vo.conversation_dto import CreateConversationDTO, CreateMessageDTO, CreateMessageContentDTO
from module_conversation.exception.conversation_exception import ConversationNotFoundException, UserPermissionException


class TestConversationDAO:
    """会话DAO测试类"""
    
    @pytest.fixture
    def conversation_dao(self):
        return ConversationDAO()
    
    @pytest.fixture
    def message_dao(self):
        return MessageDAO()
    
    @pytest.fixture
    def message_content_dao(self):
        return MessageContentDAO()
    
    @pytest.mark.asyncio
    async def test_create_conversation(self, db_session, conversation_dao):
        """测试创建会话"""
        # 创建会话
        conversation = await conversation_dao.create_conversation(
            db_session, user_id=1, title="测试会话"
        )
        
        assert conversation.user_id == 1
        assert conversation.title == "测试会话"
        assert conversation.status == 1
        assert conversation.conversation_id is not None
        
        # 验证数据库中是否存在
        found = await conversation_dao.get_conversation_by_id(
            db_session, conversation.conversation_id, user_id=1
        )
        assert found is not None
        assert found.title == "测试会话"
    
    @pytest.mark.asyncio
    async def test_get_conversations_by_user(self, db_session, conversation_dao):
        """测试按用户获取会话列表"""
        # 创建多个会话
        for i in range(5):
            await conversation_dao.create_conversation(
                db_session, user_id=1, title=f"会话{i+1}"
            )
        
        # 创建其他用户的会话
        await conversation_dao.create_conversation(
            db_session, user_id=2, title="其他用户的会话"
        )
        
        await db_session.commit()
        
        # 查询用户1的会话
        conversations, total = await conversation_dao.get_conversations_by_user(
            db_session, user_id=1, status=1, page=1, page_size=10
        )
        
        assert len(conversations) == 5
        assert total == 5
        assert all(c.user_id == 1 for c in conversations)
    
    @pytest.mark.asyncio
    async def test_update_conversation(self, db_session, conversation_dao):
        """测试更新会话"""
        # 创建会话
        conversation = await conversation_dao.create_conversation(
            db_session, user_id=1, title="原始标题"
        )
        await db_session.flush()  # 使用flush而不是commit
        
        # 更新会话
        success = await conversation_dao.update_conversation(
            db_session, conversation.conversation_id, user_id=1, title="新标题"
        )
        
        assert success is True
        await db_session.flush()  # 使用flush而不是commit
        
        # 验证更新 - 重新获取会话
        updated = await conversation_dao.get_conversation_by_id(
            db_session, conversation.conversation_id, user_id=1
        )
        assert updated is not None
        assert updated.title == "新标题"
        
        await db_session.commit()  # 最后提交
    
    @pytest.mark.asyncio
    async def test_delete_conversation(self, db_session, conversation_dao):
        """测试删除会话"""
        # 创建会话
        conversation = await conversation_dao.create_conversation(
            db_session, user_id=1, title="待删除会话"
        )
        await db_session.flush()
        
        # 删除会话
        success = await conversation_dao.delete_conversation(
            db_session, conversation.conversation_id, user_id=1
        )
        
        assert success is True
        await db_session.flush()
        
        # 验证删除
        deleted = await conversation_dao.get_conversation_by_id(
            db_session, conversation.conversation_id, user_id=1
        )
        assert deleted is None
        
        await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_permission_check(self, db_session, conversation_dao):
        """测试权限检查"""
        # 用户1创建会话
        conversation = await conversation_dao.create_conversation(
            db_session, user_id=1, title="用户1的会话"
        )
        await db_session.flush()
        
        # 用户2尝试访问
        found = await conversation_dao.get_conversation_by_id(
            db_session, conversation.conversation_id, user_id=2
        )
        assert found is None
        
        await db_session.commit()


class TestMessageDAO:
    """消息DAO测试类"""
    
    @pytest_asyncio.fixture
    async def setup_data(self, db_session, conversation_dao, message_dao):
        """设置测试数据"""
        # 创建会话
        conversation = await conversation_dao.create_conversation(
            db_session, user_id=1, title="测试会话"
        )
        await db_session.flush()
        
        return conversation
    
    @pytest.mark.asyncio
    async def test_create_message(self, db_session, message_dao, setup_data):
        """测试创建消息"""
        conversation = setup_data
        
        # 创建消息
        message = await message_dao.create_message(
            db_session, conversation_id=conversation.conversation_id, 
            role="user", seq=1
        )
        
        assert message.conversation_id == conversation.conversation_id
        assert message.role == "user"
        assert message.seq == 1
        assert message.message_id is not None
        
        await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_get_messages_by_conversation(self, db_session, message_dao, setup_data):
        """测试按会话获取消息"""
        conversation = setup_data
        
        # 创建多条消息
        for i in range(3):
            await message_dao.create_message(
                db_session, conversation_id=conversation.conversation_id,
                role="user", seq=i+1
            )
        
        await db_session.flush()
        
        # 查询消息
        messages = await message_dao.get_messages_by_conversation(
            db_session, conversation.conversation_id, user_id=1
        )
        
        assert len(messages) == 3
        assert all(m.conversation_id == conversation.conversation_id for m in messages)
        
        await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_update_message(self, db_session, message_dao, setup_data):
        """测试更新消息"""
        conversation = setup_data
        
        # 创建消息
        message = await message_dao.create_message(
            db_session, conversation_id=conversation.conversation_id,
            role="user", seq=1
        )
        await db_session.flush()
        
        # 更新消息
        success = await message_dao.update_message(
            db_session, message.message_id, role="assistant", seq=2
        )
        
        assert success is True
        await db_session.flush()
        
        # 验证更新
        updated = await message_dao.get_message_by_id(db_session, message.message_id)
        assert updated.role == "assistant"
        assert updated.seq == 2
        
        await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_delete_message(self, db_session, message_dao, setup_data):
        """测试删除消息"""
        conversation = setup_data
        
        # 创建消息
        message = await message_dao.create_message(
            db_session, conversation_id=conversation.conversation_id,
            role="user", seq=1
        )
        await db_session.flush()
        
        # 删除消息
        success = await message_dao.delete_message(db_session, message.message_id)
        
        assert success is True
        await db_session.flush()
        
        # 验证删除
        deleted = await message_dao.get_message_by_id(db_session, message.message_id)
        assert deleted is None
        
        await db_session.commit()


class TestMessageContentDAO:
    """消息内容DAO测试类"""
    
    @pytest_asyncio.fixture
    async def setup_data(self, db_session, conversation_dao, message_dao, message_content_dao):
        """设置测试数据"""
        # 创建会话
        conversation = await conversation_dao.create_conversation(
            db_session, user_id=1, title="测试会话"
        )
        
        # 创建消息
        message = await message_dao.create_message(
            db_session, conversation_id=conversation.conversation_id,
            role="user", seq=1
        )
        
        await db_session.flush()
        
        return message
    
    @pytest.mark.asyncio
    async def test_create_message_content(self, db_session, message_content_dao, setup_data):
        """测试创建消息内容"""
        message = setup_data
        
        # 创建消息内容
        content = await message_content_dao.create_message_content(
            db_session, message_id=message.message_id,
            content_type="text", text="测试消息内容", seq=1
        )
        
        assert content.message_id == message.message_id
        assert content.content_type == "text"
        assert content.text == "测试消息内容"
        assert content.seq == 1
        
        await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_batch_create_message_contents(self, db_session, message_content_dao, setup_data):
        """测试批量创建消息内容"""
        message = setup_data
        
        # 准备批量数据
        contents_data = [
            {
                "message_id": message.message_id,
                "content_type": "text",
                "text": "内容1",
                "image_url": None,
                "seq": 1
            },
            {
                "message_id": message.message_id,
                "content_type": "text",
                "text": "内容2",
                "image_url": None,
                "seq": 2
            }
        ]
        
        # 批量创建
        await message_content_dao.batch_create_message_contents(db_session, contents_data)
        await db_session.flush()
        
        # 验证创建
        contents = await message_content_dao.get_contents_by_message(
            db_session, message.message_id
        )
        
        assert len(contents) == 2
        assert contents[0].text == "内容1"
        assert contents[1].text == "内容2"
        
        await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_get_contents_by_message(self, db_session, message_content_dao, setup_data):
        """测试按消息获取内容"""
        message = setup_data
        
        # 创建多个内容
        for i in range(3):
            await message_content_dao.create_message_content(
                db_session, message_id=message.message_id,
                content_type="text", text=f"内容{i+1}", seq=i+1
            )
        
        await db_session.flush()
        
        # 查询内容
        contents = await message_content_dao.get_contents_by_message(
            db_session, message.message_id
        )
        
        assert len(contents) == 3
        assert all(c.message_id == message.message_id for c in contents)
        
        await db_session.commit()


if __name__ == "__main__":
    pytest.main([__file__])