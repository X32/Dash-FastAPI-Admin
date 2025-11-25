import asyncio
import os
from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import create_async_engine

# Load environment variables from .env.dev
from dotenv import load_dotenv
# Set APP_ENV to 'dev' to load .env.dev
os.environ['APP_ENV'] = 'dev'
# Load the config (following the same logic as config/env.py)
load_dotenv('.env.dev')

# Print current environment variables
print("--- Current Environment Variables ---")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_PORT: {os.getenv('DB_PORT')}")
print(f"DB_USERNAME: {os.getenv('DB_USERNAME')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")
print(f"DB_DATABASE: {os.getenv('DB_DATABASE')}")
print("------------------------------------")

# Test database connection
async def test_connection():
    # Build database URL
    db_url = f"mysql+asyncmy://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}"
    print(f"Database URL: {db_url}")
    
    # Create engine
    engine = create_async_engine(db_url, echo=True)
    
    try:
        # Try to connect
        async with engine.connect() as conn:
            print("Successfully connected to the database!")
            
            # Try a simple query
            result = await conn.execute(sql_text("SELECT 1"))
            row = result.fetchone()
            print(f"Query result: {row}")
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_connection())