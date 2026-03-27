# MySQL数据库操作工具类

一个功能完善的MySQL数据库操作工具类，支持Python 3.8+，提供连接管理、表结构操作、SQL执行等核心功能。

## 功能特性

### 1. 配置文件读取
- ✅ 支持从 `config.ini` 或 `.env` 配置文件读取MySQL连接参数
- ✅ 支持自定义配置文件路径
- ✅ 完善的参数验证和错误处理

### 2. MySQL连接管理
- ✅ 基于 `pymysql` 实现连接池管理
- ✅ 支持 `with` 语句上下文管理
- ✅ 自动连接/关闭，连接复用
- ✅ 详细的错误信息捕获

### 3. 表结构获取功能
- ✅ 查询指定数据库的所有表名
- ✅ 查询指定表的详细结构（字段名、类型、约束等）
- ✅ 支持格式化打印表结构
- ✅ 结果以字典/列表格式返回

### 4. 表创建功能
- ✅ 提供 `create_table()` 方法创建数据表
- ✅ 支持常见约束（主键、非空、唯一、默认值）
- ✅ 自动判断表是否存在，支持"存在则跳过"或"存在则删除重建"
- ✅ 详细的字段定义配置

### 5. 通用SQL执行功能
- ✅ 支持执行增删改查（DML/DDL）语句
- ✅ 支持参数化查询，防止SQL注入
- ✅ 查询语句返回结果集（列表+字典格式）
- ✅ 增删改语句返回影响行数
- ✅ 支持事务控制（提交、回滚）

### 6. SQL文件批量执行功能
- ✅ 读取 `.sql` 文件并批量执行
- ✅ 自动按分号分隔SQL语句
- ✅ 处理语句跨行、注释等情况
- ✅ 实时输出执行状态
- ✅ 详细的执行报告（成功/失败统计）

## 安装依赖

```bash
pip install pymysql
pip install python-dotenv  # 如果使用.env配置文件
```

## 快速开始

### 1. 配置文件

#### config.ini 格式：
```ini
[mysql]
host = localhost
port = 3306
user = root
password = your_password
database = test_db
charset = utf8mb4
connect_timeout = 30
autocommit = true
```

#### .env 格式：
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=test_db
MYSQL_CHARSET=utf8mb4
MYSQL_CONNECT_TIMEOUT=30
MYSQL_AUTOCOMMIT=true
```

### 2. 基础使用

```python
from mysql_tool import MySqlTool

# 创建数据库工具类实例（使用默认配置文件）
db = MySqlTool()

# 获取所有表
tables = db.get_tables()
print(f"数据库中的表: {tables}")

# 查看表结构
db.print_table_structure('users')
```

### 3. 创建表

```python
# 定义表结构
fields = [
    {
        'name': 'id',
        'type': 'INT',
        'primary_key': True,
        'auto_increment': True,
        'comment': '主键ID'
    },
    {
        'name': 'username',
        'type': 'VARCHAR(50)',
        'nullable': False,
        'unique': True,
        'comment': '用户名'
    },
    {
        'name': 'email',
        'type': 'VARCHAR(100)',
        'nullable': False,
        'comment': '邮箱地址'
    }
]

# 创建表
success = db.create_table('users', fields, drop_if_exists=True)
```

### 4. 执行SQL语句

```python
# 插入数据
insert_sql = "INSERT INTO users (username, email) VALUES (%s, %s)"
affected_rows = db.execute_sql(insert_sql, ('test_user', 'test@example.com'))

# 查询数据
select_sql = "SELECT * FROM users WHERE username = %s"
results = db.execute_sql(select_sql, ('test_user',))
print(f"查询结果: {results}")

# 更新数据
update_sql = "UPDATE users SET email = %s WHERE username = %s"
affected_rows = db.execute_sql(update_sql, ('new_email@example.com', 'test_user'))

# 删除数据
delete_sql = "DELETE FROM users WHERE username = %s"
affected_rows = db.execute_sql(delete_sql, ('test_user',))
```

### 5. 使用上下文管理器

```python
# 使用with语句自动管理连接
with db.get_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        print(results)
```

### 6. 批量执行SQL文件

```python
# 执行SQL文件
result = db.execute_sql_file('schema.sql', continue_on_error=True)

print(f"总语句数: {result['total']}")
print(f"成功: {result['success']}")
print(f"失败: {result['failed']}")

if result['errors']:
    print("错误详情:")
    for error in result['errors']:
        print(f"  语句{error['statement_index']}: {error['error']}")
```

### 7. 事务处理

```python
# 使用上下文管理器处理事务
with db.get_connection() as conn:
    with conn.cursor() as cursor:
        try:
            conn.begin()  # 开始事务
            
            # 执行多个操作
            cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", 
                         ('user1', 'user1@example.com'))
            cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", 
                         ('user2', 'user2@example.com'))
            
            conn.commit()  # 提交事务
            print("事务提交成功")
            
        except Exception as e:
            conn.rollback()  # 回滚事务
            print(f"事务回滚: {e}")
```

## API文档

### MySqlTool类

#### 初始化参数
- `config_path` (str, optional): 配置文件路径，默认为None（使用默认路径）
- `use_pool` (bool): 是否使用连接池，默认为True

#### 主要方法

##### 连接管理
- `connect()`: 建立数据库连接
- `close()`: 关闭数据库连接
- `get_connection()`: 获取连接的上下文管理器

##### 表结构操作
- `get_tables(database=None)`: 获取数据库中的所有表名
- `get_table_structure(table_name, database=None)`: 获取表的详细结构
- `print_table_structure(table_name, database=None)`: 格式化打印表结构

##### 表创建
- `create_table(table_name, fields, drop_if_exists=False, database=None)`: 创建数据表

##### SQL执行
- `execute_sql(sql, params=None, fetch_all=True, use_transaction=False)`: 执行SQL语句
- `execute_sql_file(file_path, encoding='utf-8', continue_on_error=True)`: 批量执行SQL文件

## 错误处理

工具类提供了完善的错误处理机制：

- 配置文件不存在或格式错误
- 数据库连接失败
- SQL语法错误
- 事务处理错误
- 文件读写错误

所有错误都会记录到日志中，并抛出相应的异常供调用方处理。

## 日志输出

支持日志输出到控制台，便于调试和问题排查。日志级别包括：
- INFO: 一般操作信息
- ERROR: 错误信息
- DEBUG: 调试信息（如SQL语句）

## 性能优化

- 使用连接池管理数据库连接
- 支持连接复用
- 参数化查询防止SQL注入
- 批量操作优化

## 安全特性

- 参数化查询防止SQL注入
- 敏感信息（密码）不在日志中显示
- 配置文件权限控制建议

## 示例代码

运行 `example_usage.py` 查看完整的使用示例：

```bash
cd /Volumes/H/testProject/kimi_k2/Dash-FastAPI-Admin/dash-fastapi-backend/module_sql
python example_usage.py
```

## 依赖说明

- **pymysql**: MySQL数据库驱动
- **python-dotenv**: 可选，用于读取.env配置文件
- **configparser**: Python标准库，用于读取ini配置文件

## 兼容性

- Python 3.8+
- MySQL 5.7+
- MariaDB 10.0+

## 注意事项

1. 使用前请确保已安装pymysql库
2. 配置文件中的数据库连接信息需要根据实际情况修改
3. 生产环境中建议使用.env文件管理敏感配置信息
4. 大数据量操作时建议使用批量处理和事务控制
5. 定期检查和优化数据库连接池配置

## 更新日志

### v1.0.0 (2024-12-29)
- 初始版本发布
- 支持所有核心功能
- 完善的错误处理和日志系统
- 详细的文档和示例代码