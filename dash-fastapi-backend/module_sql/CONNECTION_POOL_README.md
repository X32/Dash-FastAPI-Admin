# 通用数据库连接池模块

## 概述
通用数据库连接池模块，基于Python 3.8+开发，支持MySQL数据库，预留其他数据库扩展接口。核心功能包括连接复用、并发控制、资源自动释放，解决数据库连接频繁创建销毁带来的性能问题。

## 核心特性
- **连接复用**：避免频繁创建和销毁数据库连接，提升性能
- **并发控制**：支持多线程并发访问，通过锁机制保证线程安全
- **空闲连接管理**：自动维护最小/最大空闲连接数，超时空闲连接自动关闭
- **连接自动重连**：连接失败时自动重试，确保连接可用性
- **异常处理**：完善的异常处理机制，包含连接超时、连接耗尽、无效连接等场景
- **状态查询**：提供连接池状态查询接口，便于监控和调试
- **资源自动释放**：进程退出时自动关闭连接池，释放所有资源

## 配置参数

### 数据库连接配置
| 参数名 | 类型 | 必选 | 默认值 | 说明 |
|--------|------|------|--------|------|
| host | str | 是 | - | 数据库地址 |
| port | int | 是 | - | 数据库端口 |
| user | str | 是 | - | 数据库用户名 |
| password | str | 是 | - | 数据库密码 |
| database | str | 是 | - | 数据库名 |
| charset | str | 否 | 'utf8mb4' | 数据库字符集 |
| cursorclass | Cursor | 否 | DictCursor | 游标类 |
| autocommit | bool | 否 | True | 是否自动提交 |

### 连接池配置
| 参数名 | 类型 | 必选 | 默认值 | 说明 |
|--------|------|------|--------|------|
| max_connections | int | 否 | 10 | 最大连接数（最小1） |
| min_idle_connections | int | 否 | 2 | 最小空闲连接数（启动时预创建） |
| max_idle_connections | int | 否 | 5 | 最大空闲连接数（超出部分自动关闭） |
| idle_timeout | int | 否 | 300 | 空闲连接超时时间（秒，超时自动关闭） |
| connect_timeout | int | 否 | 10 | 连接数据库超时时间（秒） |
| retry_times | int | 否 | 3 | 连接失败自动重试次数 |
| blocking | bool | 否 | True | 无可用连接时是否阻塞等待 |
| wait_timeout | int | 否 | 60 | 阻塞等待超时时间（秒，仅blocking=True时生效） |

## 方法列表

### ConnectionPool类

#### 初始化方法
```python
ConnectionPool(
    config: Dict[str, Any],
    max_connections: int = 10,
    min_idle_connections: int = 2,
    max_idle_connections: int = 5,
    idle_timeout: int = 300,
    connect_timeout: int = 10,
    retry_times: int = 3,
    blocking: bool = True,
    wait_timeout: int = 60,
    logger: Optional[logging.Logger] = None
)
```

#### 获取连接
```python
get_connection() -> Connection
```
返回数据库连接对象，支持上下文管理器（`with`语句）

#### 释放连接
```python
release_connection(conn: Connection) -> None
```
将连接归还到连接池

#### 关闭连接池
```python
close() -> None
```
关闭所有空闲连接和活跃连接，释放资源

#### 获取连接池状态
```python
get_pool_status() -> Dict[str, int]
```
返回连接池当前状态，包含：
- `total_connections`: 总连接数（活跃+空闲）
- `active_connections`: 活跃连接数
- `idle_connections`: 空闲连接数
- `wait_queue_length`: 等待队列长度

#### 上下文管理器
```python
with pool.connection() as conn:
    # 使用连接执行操作
    pass
```
自动管理连接的获取和释放

### MySqlTool类扩展方法

#### 初始化方法（新增pool_config参数）
```python
MySqlTool(
    config_path: Optional[str] = None,
    use_pool: bool = True,
    pool_config: Optional[Dict[str, Any]] = None
)
```

#### 获取连接池状态
```python
get_pool_status() -> Optional[Dict[str, int]]
```
返回连接池当前状态（仅当使用连接池时有效）

## 异常类

- `ConnectionPoolError`: 连接池异常基类
- `ConnectionTimeoutError`: 连接超时异常
- `ConnectionExhaustedError`: 连接耗尽异常
- `InvalidConnectionError`: 无效连接异常

## 使用示例

### 基础使用
```python
from mysql_tool import MySqlTool

# 初始化MySQL工具类，使用默认连接池配置
db_tool = MySqlTool(use_pool=True)

# 使用连接池执行查询
with db_tool.get_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        result = cursor.fetchone()
        print(f"MySQL版本: {result['VERSION()']}")

# 获取连接池状态
pool_status = db_tool.get_pool_status()
print(f"连接池状态: {pool_status}")

# 关闭连接池
db_tool.close()
```

### 自定义连接池配置
```python
from mysql_tool import MySqlTool

# 自定义连接池配置
pool_config = {
    'max_connections': 15,
    'min_idle_connections': 3,
    'max_idle_connections': 5,
    'idle_timeout': 600,
    'connect_timeout': 15,
    'retry_times': 5
}

# 初始化MySQL工具类，使用自定义连接池配置
db_tool = MySqlTool(use_pool=True, pool_config=pool_config)

# 执行操作...

db_tool.close()
```

### 并发使用
```python
import threading
from mysql_tool import MySqlTool

db_tool = MySqlTool(use_pool=True, pool_config={'max_connections': 5})

def concurrent_task(task_id):
    with db_tool.get_connection() as conn:
        with conn.cursor() as cursor:
            # 执行查询
            cursor.execute("SELECT CONNECTION_ID()")
            result = cursor.fetchone()
            print(f"任务 {task_id} 完成，连接ID: {result['CONNECTION_ID()']}")

# 启动10个并发任务
for i in range(10):
    threading.Thread(target=concurrent_task, args=(i,)).start()
```

## 扩展接口

### 支持其他数据库
通过重写`_create_connection()`和`_validate_connection()`方法，可以扩展支持其他数据库：

```python
class PostgreSQLConnectionPool(ConnectionPool):
    def _create_connection(self) -> Optional[Connection]:
        # 实现PostgreSQL连接创建逻辑
        pass
    
    def _validate_connection(self, conn: Connection) -> bool:
        # 实现PostgreSQL连接验证逻辑
        pass
```

## 常见问题排查

### 1. 连接池耗尽
- **现象**：获取连接时抛出`ConnectionExhaustedError`异常
- **原因**：活跃连接数达到`max_connections`且无空闲连接
- **解决方法**：
  - 增加`max_connections`参数
  - 优化应用代码，减少连接占用时间
  - 检查是否有连接泄漏（未正确释放连接）

### 2. 重连失败
- **现象**：连接池初始化或获取连接时抛出连接失败异常
- **原因**：数据库服务不可用、网络中断、连接参数错误
- **解决方法**：
  - 检查数据库服务是否正常运行
  - 检查网络连接是否正常
  - 检查数据库连接参数是否正确
  - 增加`retry_times`参数，提高重连次数

### 3. 线程安全问题
- **现象**：并发访问时出现连接池状态异常或数据不一致
- **原因**：未正确使用连接池提供的线程安全接口
- **解决方法**：
  - 使用连接池提供的`get_connection()`和`release_connection()`方法
  - 优先使用上下文管理器（`with`语句）自动管理连接
  - 避免直接操作连接池内部状态

### 4. 连接超时
- **现象**：获取连接时抛出`ConnectionTimeoutError`异常
- **原因**：等待连接时间超过`wait_timeout`参数
- **解决方法**：
  - 增加`max_connections`参数
  - 优化应用代码，减少连接占用时间
  - 增加`wait_timeout`参数，延长等待时间
  - 调整`blocking`参数为False，快速失败

## 依赖安装
```bash
pip install pymysql python-dotenv
```
