import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


# 测试数据库配置 - 使用SQLite内存数据库避免asyncmy事件循环问题
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
)
TestSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


class TestBase(AsyncAttrs, DeclarativeBase):
    pass


@pytest_asyncio.fixture(scope="session")
async def test_db_engine():
    """创建测试引擎"""
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话 - 使用SQLite避免asyncmy事件循环问题"""
    # 导入主应用的Base和实体类
    from config.database import Base
    from module_conversation.entity.do.conversation_do import Conversation, Message, MessageContent
    
    # 临时替换实体类的元数据，让它们使用我们的测试引擎
    original_metadata = Base.metadata
    
    # 创建所有表
    async with test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建新会话
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        # 清理会话
        await session.close()


@pytest.fixture
def conversation_dao():
    """会话DAO"""
    from module_conversation.dao.conversation_dao import ConversationDAO
    return ConversationDAO()


@pytest.fixture
def message_dao():
    """消息DAO"""
    from module_conversation.dao.conversation_dao import MessageDAO
    return MessageDAO()


@pytest.fixture
def message_content_dao():
    """消息内容DAO"""
    from module_conversation.dao.conversation_dao import MessageContentDAO
    return MessageContentDAO()