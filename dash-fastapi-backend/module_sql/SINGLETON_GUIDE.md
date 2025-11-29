# 数据库连接池单例模式使用指南

## 概述

数据库连接池现在支持单例模式，确保在整个应用程序生命周期中，对于相同的配置只创建一个连接池实例。这有助于：

- **资源优化**：避免创建多个连接池实例，节省系统资源
- **统一管理**：所有数据库操作共享同一个连接池，便于监控和管理
- **配置一致性**：确保所有地方使用的连接池配置完全一致

## 使用方式

### 1. ConnectionPool 单例模式

```python
from connection_pool import ConnectionPool

# 首次创建单例实例
pool1 = ConnectionPool.get_instance({
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'password',
    'database': 'test_db',
    'max_connections': 10
})

# 后续获取实例（无需配置参数）
pool2 = ConnectionPool.get_instance()

# 验证是否为同一实例
print(pool1 is pool2)  # True
```

### 2. MySqlTool 集成单例模式

```python
from mysql_tool import MySqlTool

# 创建使用单例模式的MySqlTool实例
db_tool1 = MySqlTool(
    config_path='config.ini',
    use_pool=True,
    use_pool_singleton=True,  # 启用单例模式
    pool_config={
        'max_connections': 10,
        'min_idle_connections': 3,
        'max_idle_connections': 5
    }
)

# 创建第二个实例（将使用同一个连接池单例）
db_tool2 = MySqlTool(
    config_path='config.ini',
    use_pool=True,
    use_pool_singleton=True
)

# 两个实例共享同一个连接池
print(db_tool1._pool_instance is db_tool2._pool_instance)  # True
```

### 3. 便捷函数的单例模式

```python
from connection_pool import create_connection_pool

# 使用单例模式创建连接池
pool = create_connection_pool(
    config_dict={
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'password',
        'database': 'test_db'
    },
    use_singleton=True  # 启用单例模式
)
```

## 单例管理方法

### 获取单例实例
```python
# 首次创建（需要提供配置）
pool = ConnectionPool.get_instance(config_dict)

# 后续获取（无需配置）
pool = ConnectionPool.get_instance()
```

### 检查单例状态
```python
# 检查单例是否已创建
is_created = ConnectionPool.is_instance_created()
print(f"单例已创建: {is_created}")
```

### 重置单例
```python
# 重置单例（关闭现有实例）
ConnectionPool.reset_instance()

# 现在可以创建新的单例实例
new_pool = ConnectionPool.get_instance(new_config)
```

## 使用场景

### 1. Web应用
在Web应用中，通常在应用启动时创建连接池单例，整个应用生命周期中重复使用：

```python
# app.py
from connection_pool import ConnectionPool

def create_app():
    app = Flask(__name__)
    
    # 初始化连接池单例
    ConnectionPool.get_instance({
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'password',
        'database': 'myapp',
        'max_connections': 20
    })
    
    return app
```

### 2. 多模块项目
在多模块项目中，不同模块可以共享同一个连接池：

```python
# module_a.py
from connection_pool import ConnectionPool

def process_data():
    pool = ConnectionPool.get_instance()  # 获取已创建的单例
    with pool.get_connection() as conn:
        # 执行数据库操作
        pass

# module_b.py
from connection_pool import ConnectionPool

def query_data():
    pool = ConnectionPool.get_instance()  # 获取同一个单例
    with pool.get_connection() as conn:
        # 执行数据库查询
        pass
```

### 3. 微服务架构
在微服务中，每个服务实例使用一个连接池单例：

```python
# service.py
from mysql_tool import MySqlTool

class UserService:
    def __init__(self):
        self.db_tool = MySqlTool(
            use_pool=True,
            use_pool_singleton=True,  # 确保使用单例
            pool_config={'max_connections': 15}
        )
    
    def get_user(self, user_id):
        return self.db_tool.execute_sql(
            "SELECT * FROM users WHERE id = %s",
            (user_id,)
        )
```

## 注意事项

### 1. 线程安全
单例模式实现是线程安全的，可以在多线程环境中安全使用：

```python
import threading

def worker():
    pool = ConnectionPool.get_instance()  # 线程安全
    with pool.get_connection() as conn:
        # 执行数据库操作
        pass

# 启动多个线程
threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

### 2. 配置一致性
一旦单例实例创建，后续获取实例时配置参数将被忽略：

```python
# 首次创建
pool1 = ConnectionPool.get_instance({'max_connections': 10})

# 后续获取（配置参数将被忽略）
pool2 = ConnectionPool.get_instance({'max_connections': 20})  # 配置无效

print(pool1 is pool2)  # True，都是同一个实例
```

### 3. 资源清理
使用单例模式时，需要在应用关闭时正确清理资源：

```python
# 应用关闭时
def shutdown():
    # 关闭连接池单例
    if ConnectionPool.is_instance_created():
        pool = ConnectionPool.get_instance()
        pool.close()
        
    # 或者使用重置方法
    ConnectionPool.reset_instance()
```

## 性能优势

### 1. 减少连接池创建开销
```python
import time

# 普通模式（多次创建）
start = time.time()
for i in range(100):
    pool = ConnectionPool(config)  # 每次创建新实例
    pool.close()
print(f"普通模式耗时: {time.time() - start:.4f}秒")

# 单例模式（复用实例）
start = time.time()
ConnectionPool.get_instance(config)  # 创建一次
for i in range(100):
    pool = ConnectionPool.get_instance()  # 获取已存在的实例
print(f"单例模式耗时: {time.time() - start:.4f}秒")
```

### 2. 内存使用优化
单例模式避免了多个连接池实例的内存开销，特别适合资源受限的环境。

## 错误处理

```python
from connection_pool import ConnectionPool, ConnectionPoolError

try:
    # 尝试获取单例实例
    pool = ConnectionPool.get_instance(config)
    
    # 使用连接池
    with pool.get_connection() as conn:
        # 执行数据库操作
        pass
        
except ConnectionPoolError as e:
    print(f"连接池错误: {e}")
    
except Exception as e:
    print(f"其他错误: {e}")
```

## 最佳实践

1. **应用启动时初始化**：在应用启动阶段创建连接池单例
2. **配置集中管理**：将连接池配置集中管理，避免分散配置
3. **监控连接池状态**：定期监控连接池状态，及时调整配置
4. **优雅关闭**：确保应用关闭时正确关闭连接池单例
5. **错误重试**：实现连接失败时的重试机制

## 总结

连接池单例模式提供了高效、统一的数据库连接管理方式，适用于各种规模的应用程序。通过合理使用单例模式，可以显著提升应用性能，简化数据库连接管理。