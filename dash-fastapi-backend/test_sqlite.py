import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

# 测试数据库配置
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,  # 启用调试日志
    pool_pre_ping=True,
    pool_recycle=3600,
)
TestSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


class TestBase(AsyncAttrs, DeclarativeBase):
    pass


async def test_sqlite():
    try:
        # 导入模型并临时替换它们的基类
        from module_conversation.entity.do.conversation_do import Conversation, Message, MessageContent
        from config.database import Base
        
        print("Original bases:")
        for cls in [Conversation, Message, MessageContent]:
            print(f"{cls.__name__}: {cls.__bases__}")
        
        # 临时替换基类，让实体使用我们的TestBase
        original_bases = {}
        for cls in [Conversation, Message, MessageContent]:
            original_bases[cls] = cls.__bases__
            cls.__bases__ = (TestBase,)
        
        print("Modified bases:")
        for cls in [Conversation, Message, MessageContent]:
            print(f"{cls.__name__}: {cls.__bases__}")
        
        # 创建所有表
        async with test_engine.begin() as conn:
            print("Creating tables...")
            print("TestBase metadata tables:", list(TestBase.metadata.tables.keys()))
            await conn.run_sync(TestBase.metadata.create_all)
            print("Tables created successfully")
        
        # 创建新会话并测试插入
        session = TestSessionLocal()
        try:
            print("Creating conversation...")
            conversation = Conversation(user_id=1, title="测试会话", status=1, create_time=datetime.now(), update_time=datetime.now())
            session.add(conversation)
            await session.commit()
            print("Conversation created successfully")
            
        finally:
            await session.close()
            
        # 恢复原始基类
        for cls, original_base in original_bases.items():
            cls.__bases__ = original_base
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await test_engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_sqlite())