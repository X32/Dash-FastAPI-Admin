import uvicorn
import sys
import os
from config.env import GetConfig
from server import app


if __name__ == '__main__':
    # 解析命令行参数中的--env参数
    env = 'dev'
    # 收集非--env参数传递给uvicorn
    uvicorn_args = []
    for arg in sys.argv[1:]:
        if arg.startswith('--env='):
            env = arg.split('=', 1)[1]
        else:
            uvicorn_args.append(arg)
    
    # 设置环境变量
    os.environ['APP_ENV'] = env
    
    # 重新加载配置
    get_config = GetConfig()
    AppConfig = get_config.get_app_config()
    
    # 传递所有命令行参数给uvicorn
    uvicorn.run(
        app='app:app',
        host=AppConfig.app_host,
        port=AppConfig.app_port,
        root_path=AppConfig.app_root_path,
        reload=AppConfig.app_reload,
        **dict(arg.split('=', 1) for arg in uvicorn_args if '=' in arg)
    )
