import os
from dotenv import load_dotenv

print("Before loading any .env file:")
print(f"DB_USERNAME: {os.getenv('DB_USERNAME', 'NOT SET')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD', 'NOT SET')}")
print(f"DB_DATABASE: {os.getenv('DB_DATABASE', 'NOT SET')}")
print(f"APP_ENV: {os.getenv('APP_ENV', 'NOT SET')}")

# 先设置APP_ENV
os.environ['APP_ENV'] = 'dev'
print(f"\nAfter setting APP_ENV to 'dev':")
print(f"APP_ENV: {os.getenv('APP_ENV')}")

# 然后加载.env文件（根据config/env.py的逻辑）
from config.env import GetConfig

# 实例化获取配置类
get_config = GetConfig()

print(f"\nAfter loading .env.dev (based on APP_ENV=dev):")
print(f"DB_USERNAME: {os.getenv('DB_USERNAME', 'NOT SET')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD', 'NOT SET')}")
print(f"DB_DATABASE: {os.getenv('DB_DATABASE', 'NOT SET')}")

# 检查实际的配置对象值
from config.env import DataBaseConfig
print(f"\nActual DataBaseConfig values:")
print(f"DataBaseConfig.db_username: {DataBaseConfig.db_username}")
print(f"DataBaseConfig.db_password: {DataBaseConfig.db_password}")
print(f"DataBaseConfig.db_database: {DataBaseConfig.db_database}")