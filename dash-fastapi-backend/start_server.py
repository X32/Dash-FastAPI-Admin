#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动服务器脚本
"""
import uvicorn
from config.env import AppSettings

# 加载应用配置
app_settings = AppSettings()

if __name__ == "__main__":
    # 使用配置中的参数启动服务
    uvicorn.run(
        "server:app",
        host=app_settings.app_host,
        port=app_settings.app_port,
        reload=app_settings.app_reload,
        root_path=app_settings.app_root_path
    )
