# 手动运行SQL文件步骤

由于自动运行SQL文件时出现数据库访问权限问题，请按照以下步骤手动运行：

1. 打开终端，进入项目根目录：
   ```bash
   cd /Volumes/H/testProject/kimi_k2/Dash-FastAPI-Admin
   ```

2. 运行以下命令（替换为你的数据库用户名和密码）：
   ```bash
   mysql -u [你的数据库用户名] -p[你的数据库密码] -h localhost -P 3306 dash-fastapi < dash-fastapi-backend/sql/spoken_test_topic.sql
   ```

3. 执行完成后，你可以启动后端服务进行测试。
