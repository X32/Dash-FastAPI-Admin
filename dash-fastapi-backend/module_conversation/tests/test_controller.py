import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from module_conversation.controller.conversation_controller import router
from module_conversation.exception.conversation_exception import ConversationNotFoundException, UserPermissionException


class TestConversationController:
    """会话控制器测试类"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = FastAPI()
        
        # 注册异常处理器
        from module_conversation.exception import conversation_exception_handler
        app.add_exception_handler(ConversationNotFoundException, conversation_exception_handler)
        app.add_exception_handler(UserPermissionException, conversation_exception_handler)
        
        # 注册路由
        app.include_router(router)
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_db_session(self):
        """创建模拟数据库会话"""
        return AsyncMock()
    
    @patch('module_conversation.controller.conversation_controller.get_db_session')
    @patch('module_conversation.controller.conversation_controller.conversation_service')
    def test_create_conversation_success(self, mock_service, mock_db_getter, client, mock_db_session):
        """测试成功创建会话"""
        # 设置模拟
        mock_db_getter.return_value = mock_db_session
        mock_service.create_conversation = AsyncMock()
        mock_service.create_conversation.return_value = MagicMock(
            conversation_id=1,
            user_id=1,
            title="测试会话",
            status=1,
            create_time="2024-01-01 10:00:00",
            update_time="2024-01-01 10:00:00"
        )
        
        # 发送请求
        response = client.post(
            "/conversations/?user_id=1",
            json={"title": "测试会话"}
        )
        
        # 验证响应
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "测试会话"
        assert data["user_id"] == 1
    
    @patch('module_conversation.controller.conversation_controller.get_db_session')
    @patch('module_conversation.controller.conversation_controller.conversation_service')
    def test_get_conversation_list_success(self, mock_service, mock_db_getter, client, mock_db_session):
        """测试成功获取会话列表"""
        # 设置模拟
        mock_db_getter.return_value = mock_db_session
        mock_service.get_conversation_list = AsyncMock()
        mock_service.get_conversation_list.return_value = MagicMock(
            total=2,
            page=1,
            page_size=20,
            conversations=[
                MagicMock(
                    conversation_id=1,
                    user_id=1,
                    title="会话1",
                    status=1,
                    create_time="2024-01-01 10:00:00",
                    update_time="2024-01-01 10:00:00"
                ),
                MagicMock(
                    conversation_id=2,
                    user_id=1,
                    title="会话2",
                    status=1,
                    create_time="2024-01-01 11:00:00",
                    update_time="2024-01-01 11:00:00"
                )
            ]
        )
        
        # 发送请求
        response = client.get("/conversations/list?user_id=1")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["conversations"]) == 2
        assert data["conversations"][0]["title"] == "会话1"
    
    @patch('module_conversation.controller.conversation_controller.get_db_session')
    @patch('module_conversation.controller.conversation_controller.conversation_service')
    def test_get_conversation_detail_success(self, mock_service, mock_db_getter, client, mock_db_session):
        """测试成功获取会话详情"""
        # 设置模拟
        mock_db_getter.return_value = mock_db_session
        mock_service.get_conversation_detail = AsyncMock()
        mock_service.get_conversation_detail.return_value = MagicMock(
            conversation=MagicMock(
                conversation_id=1,
                user_id=1,
                title="测试会话",
                status=1,
                create_time="2024-01-01 10:00:00",
                update_time="2024-01-01 10:00:00"
            ),
            messages=[
                MagicMock(
                    message_id=1,
                    conversation_id=1,
                    role="user",
                    seq=1,
                    create_time="2024-01-01 10:00:00",
                    contents=[
                        MagicMock(
                            content_id=1,
                            message_id=1,
                            content_type="text",
                            text="测试内容",
                            seq=1
                        )
                    ]
                )
            ]
        )
        
        # 发送请求
        response = client.get("/conversations/1?user_id=1")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["conversation"]["conversation_id"] == 1
        assert data["conversation"]["title"] == "测试会话"
        assert len(data["messages"]) == 1
        assert len(data["messages"][0]["contents"]) == 1
    
    @patch('module_conversation.controller.conversation_controller.get_db_session')
    @patch('module_conversation.controller.conversation_controller.conversation_service')
    def test_update_conversation_success(self, mock_service, mock_db_getter, client, mock_db_session):
        """测试成功更新会话"""
        # 设置模拟
        mock_db_getter.return_value = mock_db_session
        mock_service.update_conversation = AsyncMock()
        mock_service.update_conversation.return_value = MagicMock(
            conversation_id=1,
            user_id=1,
            title="更新后的标题",
            status=1,
            create_time="2024-01-01 10:00:00",
            update_time="2024-01-01 12:00:00"
        )
        
        # 发送请求
        response = client.put(
            "/conversations/1?user_id=1",
            json={"title": "更新后的标题"}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "更新后的标题"
    
    @patch('module_conversation.controller.conversation_controller.get_db_session')
    @patch('module_conversation.controller.conversation_controller.conversation_service')
    def test_delete_conversation_success(self, mock_service, mock_db_getter, client, mock_db_session):
        """测试成功删除会话"""
        # 设置模拟
        mock_db_getter.return_value = mock_db_session
        mock_service.delete_conversation = AsyncMock()
        mock_service.delete_conversation.return_value = True
        
        # 发送请求
        response = client.delete("/conversations/1?user_id=1")
        
        # 验证响应
        assert response.status_code == 204
    
    @patch('module_conversation.controller.conversation_controller.get_db_session')
    @patch('module_conversation.controller.conversation_controller.conversation_service')
    def test_create_message_success(self, mock_service, mock_db_getter, client, mock_db_session):
        """测试成功创建消息"""
        # 设置模拟
        mock_db_getter.return_value = mock_db_session
        mock_service.message_service = MagicMock()
        mock_service.message_service.create_message_with_contents = AsyncMock()
        mock_service.message_service.create_message_with_contents.return_value = MagicMock(
            message_id=1,
            conversation_id=1,
            role="user",
            seq=1,
            create_time="2024-01-01 10:00:00",
            contents=[
                MagicMock(
                    content_id=1,
                    message_id=1,
                    content_type="text",
                    text="测试消息内容",
                    seq=1
                )
            ]
        )
        
        # 发送请求
        response = client.post(
            "/conversations/1/messages?user_id=1",
            json={
                "role": "user",
                "seq": 1,
                "contents": [
                    {
                        "content_type": "text",
                        "text": "测试消息内容",
                        "seq": 1
                    }
                ]
            }
        )
        
        # 验证响应
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "user"
        assert data["contents"][0]["text"] == "测试消息内容"
    
    @patch('module_conversation.controller.conversation_controller.get_db_session')
    @patch('module_conversation.controller.conversation_controller.message_service')
    def test_update_message_success(self, mock_service, mock_db_getter, client, mock_db_session):
        """测试成功更新消息"""
        # 设置模拟
        mock_db_getter.return_value = mock_db_session
        mock_service.update_message = AsyncMock()
        mock_service.update_message.return_value = MagicMock(
            message_id=1,
            conversation_id=1,
            role="assistant",
            seq=2,
            create_time="2024-01-01 10:00:00"
        )
        
        # 发送请求
        response = client.put(
            "/conversations/messages/1?user_id=1",
            json={"role": "assistant", "seq": 2}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "assistant"
        assert data["seq"] == 2
    
    @patch('module_conversation.controller.conversation_controller.get_db_session')
    @patch('module_conversation.controller.conversation_controller.message_service')
    def test_delete_message_success(self, mock_service, mock_db_getter, client, mock_db_session):
        """测试成功删除消息"""
        # 设置模拟
        mock_db_getter.return_value = mock_db_session
        mock_service.delete_message = AsyncMock()
        mock_service.delete_message.return_value = True
        
        # 发送请求
        response = client.delete("/conversations/messages/1?user_id=1")
        
        # 验证响应
        assert response.status_code == 204
    
    @patch('module_conversation.controller.conversation_controller.get_db_session')
    @patch('module_conversation.controller.conversation_controller.conversation_service')
    def test_conversation_not_found_exception(self, mock_service, mock_db_getter, client, mock_db_session):
        """测试会话不存在异常"""
        # 设置模拟抛出异常
        mock_db_getter.return_value = mock_db_session
        mock_service.get_conversation_detail = AsyncMock()
        mock_service.get_conversation_detail.side_effect = ConversationNotFoundException("会话不存在: 999")
        
        # 发送请求
        response = client.get("/conversations/999?user_id=1")
        
        # 验证响应
        assert response.status_code == 404
        data = response.json()
        assert "会话不存在" in data["message"]
        assert data["success"] is False
    
    @patch('module_conversation.controller.conversation_controller.get_db_session')
    @patch('module_conversation.controller.conversation_controller.conversation_service')
    def test_user_permission_exception(self, mock_service, mock_db_getter, client, mock_db_session):
        """测试用户权限异常"""
        # 设置模拟抛出异常
        mock_db_getter.return_value = mock_db_session
        mock_service.update_conversation = AsyncMock()
        mock_service.update_conversation.side_effect = UserPermissionException("无权访问该资源")
        
        # 发送请求
        response = client.put(
            "/conversations/1?user_id=2",
            json={"title": "新标题"}
        )
        
        # 验证响应
        assert response.status_code == 403
        data = response.json()
        assert "无权访问" in data["message"]
        assert data["success"] is False


if __name__ == "__main__":
    pytest.main([__file__])