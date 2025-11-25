import os
import sys
from dotenv import load_dotenv

# 设置APP_ENV环境变量
os.environ['APP_ENV'] = 'dev'

# 根据APP_ENV加载对应的.env文件
load_dotenv('.env.dev')

# 打印环境变量用于调试
print("--- Environment Variables ---")
print(f"DB_USERNAME: {os.getenv('DB_USERNAME', 'NOT FOUND')}")
print(f"DB_PASSWORD: {'******' if os.getenv('DB_PASSWORD') else 'NOT FOUND'}")
print(f"DB_HOST: {os.getenv('DB_HOST', 'NOT FOUND')}")
print(f"DB_PORT: {os.getenv('DB_PORT', 'NOT FOUND')}")
print(f"DB_DATABASE: {os.getenv('DB_DATABASE', 'NOT FOUND')}")
print(f"APP_ENV: {os.getenv('APP_ENV', 'dev')}")
print("----------------------------")

# 然后再导入server模块
import uvicorn
from server import app, AppConfig  # noqa: F401
from config.env import DataBaseConfig  # noqa: F401


if __name__ == '__main__':
    print(f"Using environment: {os.getenv('APP_ENV', 'dev')}")
    print(f"App Config - Name: {AppConfig.app_name}, Host: {AppConfig.app_host}, Port: {AppConfig.app_port}")
    print(f"Database Config - User: {DataBaseConfig.db_username}, Host: {DataBaseConfig.db_host}, DB: {DataBaseConfig.db_database}")
    
    # 关闭热重载以避免进程继承问题
    uvicorn.run(
        app='app:app',
        host=AppConfig.app_host,
        port=AppConfig.app_port,
        root_path=AppConfig.app_root_path,
        reload=False,
    )
