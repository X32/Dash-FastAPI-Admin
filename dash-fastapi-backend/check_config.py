import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

print("=== .env file loaded values ===")
print(f"DB_USERNAME: {os.getenv('DB_USERNAME')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")
print(f"DB_DATABASE: {os.getenv('DB_DATABASE')}")
print(f"APP_ENV: {os.getenv('APP_ENV')}")

# 导入配置
from config.env import DataBaseConfig, AppConfig

print("\n=== Python Config Object Values ===")
print(f"DataBaseConfig.db_username: {DataBaseConfig.db_username}")
print(f"DataBaseConfig.db_password: {DataBaseConfig.db_password}")
print(f"DataBaseConfig.db_database: {DataBaseConfig.db_database}")
print(f"AppConfig.app_env: {AppConfig.app_env}")