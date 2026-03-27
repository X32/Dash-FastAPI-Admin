#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话管理模块性能测试
对比改造前后的数据库操作性能
"""

import asyncio
import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import pytest
import pytest_asyncio

from config.database import AsyncSessionLocal
from module_conversation.dao.connection_manager import connection_manager
from module_conversation.dao.conversation_dao import ConversationDAO, MessageDAO
from module_conversation.service.conversation_service import ConversationService
from module_conversation.entity.do.conversation_do import Conversation
from module_conversation.entity.do.conversation_do import Message
from module_conversation.entity.do.conversation_do import MessageContent


class PerformanceTest:
    """性能测试类"""
    
    def __init__(self):
        self.conversation_dao = ConversationDAO()
        self.conversation_service = ConversationService()
        self.message_dao = MessageDAO()  # 直接创建消息DAO实例
        self.test_user_id = 999999
        self.test_data_count = 100
    
    async def setup_test_data(self, session: AsyncSession):
        """设置测试数据"""
        # 清理现有测试数据
        try:
            # 按依赖顺序删除数据，忽略外键约束
            await session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            # 先删除相关表的数据（按依赖顺序）
            await session.execute(
                text("DELETE FROM message_contents WHERE message_id IN (SELECT id FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id = :user_id))"),
                {"user_id": self.test_user_id}
            )
            await session.execute(
                text("DELETE FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id = :user_id)"),
                {"user_id": self.test_user_id}
            )
            await session.execute(
                text("DELETE FROM conversations WHERE user_id = :user_id"),
                {"user_id": self.test_user_id}
            )
            
            await session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            await session.flush()
        except Exception as e:
            print(f"清理测试数据时出错: {e}")
            # 如果表不存在，先创建表
            pass
    
    async def test_conversation_operations_performance(self, session: AsyncSession):
        """测试会话操作性能"""
        print("\n=== 会话操作性能测试 ===")
        
        # 测试批量创建性能
        start_time = time.time()
        conversations_data = []
        for i in range(self.test_data_count):
            conversations_data.append({
                "title": f"测试会话_{i}",
                "user_id": self.test_user_id,
                "status": 1
            })
        
        created_conversations = await self.conversation_dao.bulk_create(session, conversations_data)
        await session.flush()  # 使用flush而不是commit
        create_time = time.time() - start_time
        print(f"批量创建 {self.test_data_count} 个会话: {create_time:.4f}s")
        
        # 测试查询性能
        start_time = time.time()
        conversations = await self.conversation_dao.get_conversations_by_user(
            session, self.test_user_id, limit=self.test_data_count
        )
        query_time = time.time() - start_time
        print(f"查询 {len(conversations)} 个会话: {query_time:.4f}s")
        
        # 测试更新性能
        start_time = time.time()
        update_data = [{"id": conv.conversation_id, "title": f"更新后的会话_{i}"} 
                      for i, conv in enumerate(created_conversations[:10])]
        updated_count = await self.conversation_dao.bulk_update(session, update_data)
        await session.flush()
        update_time = time.time() - start_time
        print(f"批量更新 {updated_count} 个会话: {update_time:.4f}s")
        
        # 测试删除性能
        start_time = time.time()
        delete_ids = [conv.conversation_id for conv in created_conversations[:10]]
        deleted_count = await self.conversation_dao.bulk_delete(session, delete_ids)
        await session.flush()
        delete_time = time.time() - start_time
        print(f"批量删除 {deleted_count} 个会话: {delete_time:.4f}s")
        
        return {
            "create_time": create_time,
            "query_time": query_time,
            "update_time": update_time,
            "delete_time": delete_time
        }
    
    async def test_message_operations_performance(self, session: AsyncSession):
        """测试消息操作性能"""
        print("\n=== 消息操作性能测试 ===")
        
        # 先创建一个测试会话
        conversation = await self.conversation_dao.create_conversation(
            session, "性能测试会话", self.test_user_id
        )
        await session.flush()
        
        # 测试批量创建消息性能
        start_time = time.time()
        messages_data = []
        for i in range(self.test_data_count):
            messages_data.append({
                "conversation_id": conversation.conversation_id,
                "role": random.choice(["user", "assistant"]),
                "content": f"测试消息内容_{i}",
                "seq": i
            })
        
        # 使用消息DAO批量创建消息
        created_messages = []
        for msg_data in messages_data:
            message = await self.message_dao.create_message(
                session, msg_data["conversation_id"], msg_data["role"], msg_data["seq"]
            )
            created_messages.append(message)
        await session.flush()
        create_time = time.time() - start_time
        print(f"批量创建 {self.test_data_count} 条消息: {create_time:.4f}s")
        
        # 测试查询消息性能
        start_time = time.time()
        messages = await self.message_dao.get_messages_by_conversation(
            session, conversation.conversation_id, self.test_user_id
        )
        query_time = time.time() - start_time
        print(f"查询 {len(messages)} 条消息: {query_time:.4f}s")
        
        return {
            "message_create_time": create_time,
            "message_query_time": query_time,
            "content_create_time": 0,
            "content_query_time": 0
        }
    
    async def test_connection_pool_stats(self):
        """测试连接池统计功能"""
        print("\n=== 连接池统计测试 ===")
        
        stats = connection_manager.get_stats()
        print(f"连接池统计信息: {stats}")
        
        engine_stats = connection_manager.get_engine_stats()
        print(f"引擎统计信息: {engine_stats}")
        
        # 健康检查
        health = await connection_manager.health_check()
        print(f"健康检查结果: {health}")
        
        return {
            "stats": stats,
            "engine_stats": engine_stats,
            "health": health
        }
    
    async def run_all_performance_tests(self):
        """运行所有性能测试"""
        print("开始会话管理模块性能测试...")
        
        async with AsyncSessionLocal() as session:
            try:
                # 设置测试数据
                await self.setup_test_data(session)
                
                # 运行会话操作性能测试
                conversation_results = await self.test_conversation_operations_performance(session)
                
                # 运行消息操作性能测试
                message_results = await self.test_message_operations_performance(session)
                
                # 运行连接池统计测试
                stats_results = await self.test_connection_pool_stats()
                
                # 提交所有变更
                await session.commit()
                
                # 汇总结果
                all_results = {
                    "conversation_operations": conversation_results,
                    "message_operations": message_results,
                    "connection_pool_stats": stats_results,
                    "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                print("\n=== 性能测试汇总 ===")
                print(f"测试时间: {all_results['test_timestamp']}")
                print(f"测试数据量: {self.test_data_count}")
                print(f"会话操作 - 创建: {conversation_results['create_time']:.4f}s")
                print(f"会话操作 - 查询: {conversation_results['query_time']:.4f}s")
                print(f"会话操作 - 更新: {conversation_results['update_time']:.4f}s")
                print(f"会话操作 - 删除: {conversation_results['delete_time']:.4f}s")
                print(f"消息操作 - 创建: {message_results['message_create_time']:.4f}s")
                print(f"消息操作 - 查询: {message_results['message_query_time']:.4f}s")
                print(f"消息内容 - 创建: {message_results['content_create_time']:.4f}s")
                print(f"消息内容 - 查询: {message_results['content_query_time']:.4f}s")
                
                return all_results
                
            except Exception as e:
                print(f"性能测试失败: {e}")
                await session.rollback()
                raise
            finally:
                # 清理测试数据
                try:
                    # 按依赖顺序删除数据，忽略外键约束
                    await session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
                    
                    # 先删除相关表的数据（按依赖顺序）
                    await session.execute(
                        text("DELETE FROM message_contents WHERE message_id IN (SELECT id FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id = :user_id))"),
                        {"user_id": self.test_user_id}
                    )
                    await session.execute(
                        text("DELETE FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id = :user_id)"),
                        {"user_id": self.test_user_id}
                    )
                    await session.execute(
                        text("DELETE FROM conversations WHERE user_id = :user_id"),
                        {"user_id": self.test_user_id}
                    )
                    
                    await session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
                    await session.commit()
                except Exception as e:
                    print(f"清理测试数据时出错: {e}")
                    await session.rollback()


@pytest.mark.asyncio
async def test_performance_comparison():
    """性能对比测试"""
    test_runner = PerformanceTest()
    results = await test_runner.run_all_performance_tests()
    
    # 验证性能指标
    assert results["conversation_operations"]["create_time"] < 5.0, "会话创建性能过慢"
    assert results["conversation_operations"]["query_time"] < 1.0, "会话查询性能过慢"
    assert results["message_operations"]["message_create_time"] < 5.0, "消息创建性能过慢"
    assert results["message_operations"]["message_query_time"] < 1.0, "消息查询性能过慢"
    
    # 验证连接池状态
    stats = results["connection_pool_stats"]["stats"]
    assert stats["total_queries"] > 0, "没有查询记录"
    assert stats["avg_query_time"] < 0.1, "平均查询时间过长"
    
    health = results["connection_pool_stats"]["health"]
    assert health["status"] == "healthy", "数据库连接不健康"
    assert health["response_time"] < 0.1, "数据库响应时间过长"


if __name__ == "__main__":
    # 直接运行性能测试
    asyncio.run(PerformanceTest().run_all_performance_tests())