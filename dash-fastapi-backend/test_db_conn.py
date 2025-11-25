import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from urllib.parse import quote_plus

# 使用.env文件中的配置
DB_USERNAME = 'root'
DB_PASSWORD = 'X12345678x'
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_DATABASE = 'dash_fastapi'

# 创建数据库URL
DATABASE_URL = (
    f'mysql+asyncmy://{DB_USERNAME}:{quote_plus(DB_PASSWORD)}@'
    f'{DB_HOST}:{DB_PORT}/{DB_DATABASE}'
)

print(f"Testing connection to: {DATABASE_URL.replace(quote_plus(DB_PASSWORD), '******')}")

async def test_connection():
    try:
        engine = create_async_engine(DATABASE_URL)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            print(f"Result: {result.fetchone()}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    finally:
        if 'engine' in locals():
            await engine.dispose()

if __name__ == '__main__':
    asyncio.run(test_connection())