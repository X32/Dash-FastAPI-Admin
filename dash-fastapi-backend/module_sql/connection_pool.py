#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用数据库连接池模块类
兼容Python 3.8+
核心依赖：pymysql
可选依赖：configparser, python-dotenv

@author: AI Assistant
@created: 2024-12-29
"""

import os
import time
import logging
import threading
import configparser
from typing import Dict, List, Optional, Union, Any, Set
from contextlib import contextmanager
from datetime import datetime, timedelta
from queue import Queue, Empty

import pymysql
from pymysql.connections import Connection
from pymysql.cursors import DictCursor
from pymysql.err import OperationalError, InterfaceError


class ConnectionPoolError(Exception):
    """连接池自定义异常类"""
    
    def __init__(self, message: str, pool_status: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.pool_status = pool_status or {}
        self.timestamp = datetime.now()
    
    def __str__(self):
        status_info = f"\n连接池状态: {self.pool_status}" if self.pool_status else ""
        return f"{self.args[0]}{status_info}\n时间: {self.timestamp}"


class PooledConnection:
    """池化连接包装类，用于自动归还连接到池中"""
    
    def __init__(self, connection: Connection, pool: 'ConnectionPool'):
        self._connection = connection
        self._pool = pool
        self._in_use = True
        self._created_at = datetime.now()
        self._last_used = datetime.now()
        self._use_count = 0
    
    def __enter__(self):
        return self._connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """归还连接到池中，而不是真正关闭连接"""
        if self._in_use and self._pool:
            self._pool._return_connection(self)
            self._in_use = False
    
    def get_raw_connection(self) -> Connection:
        """获取原始连接对象"""
        return self._connection
    
    def is_expired(self, idle_timeout: int) -> bool:
        """检查连接是否过期"""
        if not self._in_use:
            idle_time = (datetime.now() - self._last_used).total_seconds()
            return idle_time > idle_timeout
        return False
    
    def is_valid(self) -> bool:
        """验证连接是否有效"""
        try:
            if self._connection and self._connection.open:
                self._connection.ping(reconnect=False)
                return True
        except Exception:
            pass
        return False


class ConnectionPool:
    """通用数据库连接池类 - 支持单例模式"""
    
    # 单例实例存储
    _instance: Optional['ConnectionPool'] = None
    _instance_lock = threading.Lock()
    
    # 默认配置参数
    DEFAULT_CONFIG = {
        'max_connections': 10,           # 最大连接数
        'min_idle_connections': 2,         # 最小空闲连接数
        'max_idle_connections': 5,         # 最大空闲连接数
        'idle_timeout': 300,              # 空闲连接超时时间（秒）
        'connect_timeout': 10,              # 连接超时时间（秒）
        'retry_times': 3,                   # 重试次数
        'retry_interval': 1,               # 重试间隔（秒）
        'blocking': True,                  # 是否阻塞等待
        'wait_timeout': 60,                # 等待超时时间（秒）
        'health_check_interval': 60,     # 健康检查间隔（秒）
        'charset': 'utf8mb4',              # 字符集
        'autocommit': True,                # 自动提交
        'cursorclass': DictCursor          # 游标类型
    }
    
    def __new__(cls, config: Optional[Union[Dict[str, Any], str]] = None, **kwargs):
        """
        单例模式实现 - 确保同一配置只创建一个连接池实例
        
        Args:
            config: 配置字典或配置文件路径
            **kwargs: 额外的配置参数
            
        Returns:
            ConnectionPool: 单例实例
        """
        # 如果没有实例或者提供了新的配置，则创建新实例
        if cls._instance is None or config is not None:
            with cls._instance_lock:
                # 双重检查锁定
                if cls._instance is None or config is not None:
                    # 创建新实例
                    instance = super().__new__(cls)
                    cls._instance = instance
        
        return cls._instance
    
    def __init__(self, config: Optional[Union[Dict[str, Any], str]] = None, **kwargs):
        """
        初始化连接池
        
        Args:
            config: 配置字典或配置文件路径
            **kwargs: 额外的配置参数
        """
        # 防止单例模式下的重复初始化
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.logger = self._setup_logger()
        self.config = self._load_config(config, **kwargs)
        
        # 连接池状态
        self._pool: Queue = Queue()                    # 空闲连接队列
        self._active_connections: Set[PooledConnection] = set()  # 活跃连接集合
        self._pool_lock = threading.RLock()            # 线程锁
        self._closed = False                           # 连接池是否已关闭
        self._shutdown_event = threading.Event()       # 关闭事件信号
        self._total_created = 0                        # 总创建连接数
        self._total_destroyed = 0                    # 总销毁连接数
        
        # 统计信息
        self._stats = {
            'total_requests': 0,      # 总请求数
            'hit_count': 0,           # 命中数
            'miss_count': 0,            # 未命中数
            'wait_time': 0,             # 总等待时间
            'create_time': 0            # 总创建时间
        }
        
        # 初始化连接池
        self._initialize_pool()
        
        # 启动后台线程
        self._start_background_threads()
        
        # 标记为已初始化
        self._initialized = True
        
        self.logger.info(f"连接池初始化完成: {self.get_pool_status()}")
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志配置"""
        logger = logging.getLogger(f"{__name__}.ConnectionPool")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _load_config(self, config: Optional[Union[Dict[str, Any], str]], **kwargs) -> Dict[str, Any]:
        """加载配置"""
        final_config = self.DEFAULT_CONFIG.copy()
        
        # 从配置文件加载
        if isinstance(config, str) and os.path.exists(config):
            file_config = self._load_config_from_file(config)
            final_config.update(file_config)
        elif isinstance(config, dict):
            final_config.update(config)
        
        # 从kwargs加载
        final_config.update(kwargs)
        
        # 验证必要参数
        required_params = ['host', 'user', 'password', 'database']
        missing_params = [param for param in required_params if not final_config.get(param)]
        if missing_params:
            raise ConnectionPoolError(f"缺少必要的数据库连接参数: {missing_params}")
        
        # 验证数值参数
        self._validate_numeric_config(final_config)
        
        return final_config
    
    def _load_config_from_file(self, config_path: str) -> Dict[str, Any]:
        """从配置文件加载配置"""
        config = {}
        
        try:
            if config_path.endswith('.ini'):
                config = self._load_ini_config(config_path)
            elif config_path.endswith('.env'):
                config = self._load_env_config(config_path)
            else:
                self.logger.warning(f"不支持的配置文件格式: {config_path}")
                
        except Exception as e:
            self.logger.error(f"配置文件加载失败: {str(e)}")
            
        return config
    
    def _load_ini_config(self, config_path: str) -> Dict[str, Any]:
        """加载INI配置文件"""
        parser = configparser.ConfigParser()
        parser.read(config_path, encoding='utf-8')
        
        # 支持的section名称
        sections = ['mysql', 'database', 'db', 'connection_pool', 'pool']
        target_section = None
        
        for section in sections:
            if section in parser.sections():
                target_section = section
                break
        
        if not target_section:
            return {}
        
        section_config = parser[target_section]
        config = {}
        
        # 数据库连接参数
        if section_config.get('host'):
            config['host'] = section_config.get('host')
        if section_config.get('port'):
            config['port'] = int(section_config.get('port'))
        if section_config.get('user'):
            config['user'] = section_config.get('user')
        if section_config.get('password'):
            config['password'] = section_config.get('password')
        if section_config.get('database'):
            config['database'] = section_config.get('database')
        
        # 连接池参数
        if section_config.get('max_connections'):
            config['max_connections'] = int(section_config.get('max_connections'))
        if section_config.get('min_idle_connections'):
            config['min_idle_connections'] = int(section_config.get('min_idle_connections'))
        if section_config.get('max_idle_connections'):
            config['max_idle_connections'] = int(section_config.get('max_idle_connections'))
        if section_config.get('idle_timeout'):
            config['idle_timeout'] = int(section_config.get('idle_timeout'))
        if section_config.get('connect_timeout'):
            config['connect_timeout'] = int(section_config.get('connect_timeout'))
        if section_config.get('retry_times'):
            config['retry_times'] = int(section_config.get('retry_times'))
        if section_config.get('blocking'):
            config['blocking'] = section_config.getboolean('blocking')
        if section_config.get('wait_timeout'):
            config['wait_timeout'] = int(section_config.get('wait_timeout'))
        
        return config
    
    def _load_env_config(self, config_path: str) -> Dict[str, Any]:
        """加载环境变量配置文件"""
        from dotenv import load_dotenv
        load_dotenv(config_path)
        
        config = {}
        
        # 数据库连接参数
        if os.getenv('MYSQL_HOST'):
            config['host'] = os.getenv('MYSQL_HOST')
        if os.getenv('MYSQL_PORT'):
            config['port'] = int(os.getenv('MYSQL_PORT'))
        if os.getenv('MYSQL_USER'):
            config['user'] = os.getenv('MYSQL_USER')
        if os.getenv('MYSQL_PASSWORD'):
            config['password'] = os.getenv('MYSQL_PASSWORD')
        if os.getenv('MYSQL_DATABASE'):
            config['database'] = os.getenv('MYSQL_DATABASE')
        
        # 连接池参数
        if os.getenv('POOL_MAX_CONNECTIONS'):
            config['max_connections'] = int(os.getenv('POOL_MAX_CONNECTIONS'))
        if os.getenv('POOL_MIN_IDLE_CONNECTIONS'):
            config['min_idle_connections'] = int(os.getenv('POOL_MIN_IDLE_CONNECTIONS'))
        if os.getenv('POOL_MAX_IDLE_CONNECTIONS'):
            config['max_idle_connections'] = int(os.getenv('POOL_MAX_IDLE_CONNECTIONS'))
        if os.getenv('POOL_IDLE_TIMEOUT'):
            config['idle_timeout'] = int(os.getenv('POOL_IDLE_TIMEOUT'))
        if os.getenv('POOL_CONNECT_TIMEOUT'):
            config['connect_timeout'] = int(os.getenv('POOL_CONNECT_TIMEOUT'))
        if os.getenv('POOL_RETRY_TIMES'):
            config['retry_times'] = int(os.getenv('POOL_RETRY_TIMES'))
        if os.getenv('POOL_BLOCKING'):
            config['blocking'] = os.getenv('POOL_BLOCKING').lower() == 'true'
        if os.getenv('POOL_WAIT_TIMEOUT'):
            config['wait_timeout'] = int(os.getenv('POOL_WAIT_TIMEOUT'))
        
        return config
    
    def _validate_numeric_config(self, config: Dict[str, Any]) -> None:
        """验证数值配置参数"""
        # 验证连接池参数
        max_conn = config.get('max_connections', 10)
        min_idle = config.get('min_idle_connections', 2)
        max_idle = config.get('max_idle_connections', 5)
        
        if max_conn < 1:
            raise ConnectionPoolError("max_connections 必须大于等于 1")
        
        if min_idle < 0:
            raise ConnectionPoolError("min_idle_connections 必须大于等于 0")
        
        if max_idle < min_idle:
            raise ConnectionPoolError("max_idle_connections 必须大于等于 min_idle_connections")
        
        if max_conn < max_idle:
            raise ConnectionPoolError("max_connections 必须大于等于 max_idle_connections")
    
    def _initialize_pool(self) -> None:
        """初始化连接池"""
        min_idle = self.config['min_idle_connections']
        
        self.logger.info(f"开始初始化连接池，预创建 {min_idle} 个连接")
        
        for i in range(min_idle):
            try:
                conn = self._create_connection()
                pooled_conn = PooledConnection(conn, self)
                self._pool.put(pooled_conn)
                self._total_created += 1
                self.logger.debug(f"预创建连接 {i+1}/{min_idle} 成功")
            except Exception as e:
                self.logger.error(f"预创建连接 {i+1}/{min_idle} 失败: {str(e)}")
                raise ConnectionPoolError(f"连接池初始化失败: {str(e)}")
    
    def _start_background_threads(self) -> None:
        """启动后台线程"""
        # 健康检查线程
        self._health_check_thread = threading.Thread(
            target=self._health_check_worker,
            daemon=True,
            name="ConnectionPool-HealthCheck"
        )
        self._health_check_thread.start()
        
        self.logger.info("后台线程启动完成")
    
    def _create_connection(self) -> Connection:
        """创建新的数据库连接"""
        connection_params = {
            'host': self.config['host'],
            'port': self.config['port'],
            'user': self.config['user'],
            'password': self.config['password'],
            'database': self.config['database'],
            'charset': self.config['charset'],
            'connect_timeout': self.config['connect_timeout'],
            'cursorclass': self.config['cursorclass'],
            'autocommit': self.config['autocommit']
        }
        
        # 重试机制
        for attempt in range(self.config['retry_times']):
            try:
                start_time = time.time()
                conn = pymysql.connect(**connection_params)
                create_time = time.time() - start_time
                self._stats['create_time'] += create_time
                
                self.logger.debug(f"数据库连接创建成功 (尝试 {attempt + 1})")
                return conn
                
            except Exception as e:
                self.logger.warning(f"数据库连接创建失败 (尝试 {attempt + 1}): {str(e)}")
                if attempt < self.config['retry_times'] - 1:
                    time.sleep(self.config['retry_interval'])
                else:
                    raise ConnectionPoolError(f"数据库连接创建失败，已重试 {self.config['retry_times']} 次: {str(e)}")
    
    def _validate_connection(self, conn: Connection) -> bool:
        """验证连接有效性"""
        try:
            if conn and conn.open:
                conn.ping(reconnect=False)
                return True
        except Exception as e:
            self.logger.debug(f"连接验证失败: {str(e)}")
        return False
    
    def get_connection(self, timeout: Optional[float] = None) -> PooledConnection:
        """
        从连接池获取连接
        
        Args:
            timeout: 获取连接的超时时间（秒），None则使用配置中的wait_timeout
            
        Returns:
            PooledConnection: 池化连接对象
            
        Raises:
            ConnectionPoolError: 连接池已关闭或无法获取连接
        """
        if self._closed:
            raise ConnectionPoolError("连接池已关闭")
        
        timeout = timeout or self.config['wait_timeout']
        start_time = time.time()
        
        with self._pool_lock:
            self._stats['total_requests'] += 1
            
            # 尝试从池中获取连接
            pooled_conn = self._get_connection_from_pool()
            if pooled_conn:
                self._stats['hit_count'] += 1
                self.logger.debug(f"从连接池获取连接成功")
                return pooled_conn
            
            # 如果未达到最大连接数，创建新连接
            if len(self._active_connections) < self.config['max_connections']:
                try:
                    conn = self._create_connection()
                    pooled_conn = PooledConnection(conn, self)
                    self._active_connections.add(pooled_conn)
                    self._total_created += 1
                    self.logger.debug(f"创建新连接成功")
                    return pooled_conn
                except Exception as e:
                    self.logger.error(f"创建新连接失败: {str(e)}")
                    raise ConnectionPoolError(f"创建新连接失败: {str(e)}", self.get_pool_status())
            
            # 无法创建新连接，根据blocking参数决定行为
            if not self.config['blocking']:
                self._stats['miss_count'] += 1
                raise ConnectionPoolError(
                    f"连接池已满（最大连接数：{self.config['max_connections']}），无法获取连接",
                    self.get_pool_status()
                )
            
            # 阻塞等待可用连接
            self.logger.debug(f"连接池已满，开始阻塞等待（超时：{timeout}秒）")
            
        # 在锁外等待，避免阻塞其他线程
        try:
            pooled_conn = self._pool.get(timeout=timeout)
            pooled_conn._in_use = True
            pooled_conn._last_used = datetime.now()
            pooled_conn._use_count += 1
            self._active_connections.add(pooled_conn)
            self.logger.debug(f"阻塞等待获取连接成功")
            return pooled_conn
            
        except Empty:
            wait_time = time.time() - start_time
            self._stats['wait_time'] += wait_time
            self._stats['miss_count'] += 1
            raise ConnectionPoolError(
                f"获取连接超时（等待时间：{wait_time:.2f}秒）",
                self.get_pool_status()
            )
    
    def _get_connection_from_pool(self) -> Optional[PooledConnection]:
        """从连接池获取连接"""
        while not self._pool.empty():
            try:
                pooled_conn = self._pool.get_nowait()
                
                # 验证连接有效性
                if pooled_conn.is_valid() and not pooled_conn.is_expired(self.config['idle_timeout']):
                    pooled_conn._in_use = True
                    pooled_conn._last_used = datetime.now()
                    pooled_conn._use_count += 1
                    self._active_connections.add(pooled_conn)
                    return pooled_conn
                else:
                    # 连接无效或已过期，销毁并继续尝试
                    self._destroy_connection(pooled_conn)
                    
            except Empty:
                break
                
        return None
    
    def _return_connection(self, pooled_conn: PooledConnection) -> None:
        """归还连接到池中"""
        if self._closed:
            self._destroy_connection(pooled_conn)
            return
        
        with self._pool_lock:
            if pooled_conn in self._active_connections:
                self._active_connections.remove(pooled_conn)
            
            # 验证连接有效性
            if not pooled_conn.is_valid():
                self._destroy_connection(pooled_conn)
                return
            
            # 如果空闲连接数已达到上限，销毁连接
            if self._pool.qsize() >= self.config['max_idle_connections']:
                self._destroy_connection(pooled_conn)
                return
            
            # 归还到池中
            pooled_conn._in_use = False
            self._pool.put(pooled_conn)
            self.logger.debug("连接归还成功")
    
    def _destroy_connection(self, pooled_conn: PooledConnection) -> None:
        """销毁连接"""
        try:
            if pooled_conn._connection and pooled_conn._connection.open:
                pooled_conn._connection.close()
            self._total_destroyed += 1
            self.logger.debug("连接销毁成功")
        except Exception as e:
            self.logger.warning(f"连接销毁失败: {str(e)}")
    
    def _health_check_worker(self) -> None:
        """健康检查后台线程"""
        self.logger.info("健康检查线程启动")
        
        while not self._closed:
            try:
                # 使用Event.wait替代time.sleep，支持即时唤醒
                if self._shutdown_event.wait(timeout=self.config['health_check_interval']):
                    # 事件被设置，表示需要关闭
                    break
                
                if self._closed:
                    break
                
                self._perform_health_check()
                
            except Exception as e:
                self.logger.error(f"健康检查异常: {str(e)}")
        
        self.logger.info("健康检查线程已退出")
    
    def _perform_health_check(self) -> None:
        """执行健康检查"""
        self.logger.debug("开始健康检查")
        
        with self._pool_lock:
            # 检查并清理过期连接
            connections_to_check = []
            
            # 收集所有空闲连接
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    connections_to_check.append(conn)
                except Empty:
                    break
            
            # 验证每个连接
            valid_connections = []
            for conn in connections_to_check:
                if conn.is_valid() and not conn.is_expired(self.config['idle_timeout']):
                    valid_connections.append(conn)
                else:
                    self._destroy_connection(conn)
            
            # 将有效连接放回池中
            for conn in valid_connections:
                self._pool.put(conn)
            
            # 补充最小空闲连接数
            current_idle = len(valid_connections)
            min_idle = self.config['min_idle_connections']
            
            if current_idle < min_idle and len(self._active_connections) < self.config['max_connections']:
                needed = min(min_idle - current_idle, self.config['max_connections'] - len(self._active_connections))
                
                for i in range(needed):
                    try:
                        conn = self._create_connection()
                        pooled_conn = PooledConnection(conn, self)
                        self._pool.put(pooled_conn)
                        self._total_created += 1
                        self.logger.debug(f"健康检查补充连接 {i+1}/{needed} 成功")
                    except Exception as e:
                        self.logger.error(f"健康检查补充连接失败: {str(e)}")
                        break
        
        self.logger.debug("健康检查完成")
    
    def get_pool_status(self) -> Dict[str, Any]:
        """
        获取连接池状态
        
        Returns:
            Dict: 连接池状态信息
        """
        with self._pool_lock:
            return {
                'total_connections': self._total_created - self._total_destroyed,
                'active_connections': len(self._active_connections),
                'idle_connections': self._pool.qsize(),
                'max_connections': self.config['max_connections'],
                'min_idle_connections': self.config['min_idle_connections'],
                'max_idle_connections': self.config['max_idle_connections'],
                'total_created': self._total_created,
                'total_destroyed': self._total_destroyed,
                'pool_closed': self._closed,
                'statistics': self._stats.copy()
            }
    
    def close(self, timeout: Optional[float] = None) -> None:
        """
        关闭连接池
        
        Args:
            timeout: 关闭超时时间（秒）
        """
        if self._closed:
            return
        
        self.logger.info("开始关闭连接池")
        self._closed = True
        # 设置关闭事件，唤醒健康检查线程
        self._shutdown_event.set()
        
        timeout = timeout or self.config['wait_timeout']
        start_time = time.time()
        
        try:
            # 等待活跃连接归还（带超时）
            while len(self._active_connections) > 0 and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            # 强制关闭剩余活跃连接
            with self._pool_lock:
                for conn in list(self._active_connections):
                    self._destroy_connection(conn)
                self._active_connections.clear()
                
                # 关闭所有空闲连接
                while not self._pool.empty():
                    try:
                        conn = self._pool.get_nowait()
                        self._destroy_connection(conn)
                    except Empty:
                        break
            
            self.logger.info(f"连接池已关闭: {self.get_pool_status()}")
            
        except Exception as e:
            self.logger.error(f"关闭连接池时出错: {str(e)}")
            raise ConnectionPoolError(f"关闭连接池失败: {str(e)}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    def __del__(self):
        """析构函数"""
        try:
            self.close(timeout=5)
        except Exception:
            pass
    
    @classmethod
    def get_instance(cls, config: Optional[Union[Dict[str, Any], str]] = None, **kwargs) -> 'ConnectionPool':
        """
        获取连接池单例实例
        
        Args:
            config: 配置字典或配置文件路径（首次创建时使用）
            **kwargs: 额外的配置参数（首次创建时使用）
            
        Returns:
            ConnectionPool: 连接池单例实例
            
        Example:
            # 首次创建实例
            pool = ConnectionPool.get_instance({
                'host': 'localhost',
                'user': 'root',
                'password': 'password',
                'database': 'test_db'
            })
            
            # 后续获取同一实例
            pool2 = ConnectionPool.get_instance()  # 返回同一个实例
        """
        if cls._instance is None and config is None:
            raise ConnectionPoolError("连接池单例尚未创建，请提供配置参数进行初始化")
        
        return cls(config, **kwargs)
    
    @classmethod
    def reset_instance(cls) -> None:
        """
        重置连接池单例（用于测试或重新配置）
        
        注意：此方法会关闭现有的连接池实例
        """
        if cls._instance is not None:
            try:
                cls._instance.close()
            except Exception as e:
                logging.warning(f"关闭现有连接池实例时出错: {e}")
            finally:
                cls._instance = None
    
    @classmethod
    def is_instance_created(cls) -> bool:
        """
        检查连接池单例是否已创建
        
        Returns:
            bool: True 如果单例已创建，否则 False
        """
        return cls._instance is not None


# 便捷函数
def create_connection_pool(config: Optional[Union[Dict[str, Any], str]] = None, use_singleton: bool = False, **kwargs) -> ConnectionPool:
    """
    创建连接池的便捷函数
    
    Args:
        config: 配置字典或配置文件路径
        use_singleton: 是否使用单例模式（默认False）
        **kwargs: 额外的配置参数
        
    Returns:
        ConnectionPool: 连接池实例
        
    Example:
        # 普通模式（每次创建新实例）
        pool1 = create_connection_pool(config)
        pool2 = create_connection_pool(config)  # 不同的实例
        
        # 单例模式（返回同一实例）
        pool1 = create_connection_pool(config, use_singleton=True)
        pool2 = create_connection_pool(config, use_singleton=True)  # 同一个实例
    """
    if use_singleton:
        return ConnectionPool.get_instance(config, **kwargs)
    else:
        return ConnectionPool(config, **kwargs)


@contextmanager
def get_pooled_connection(pool: ConnectionPool, timeout: Optional[float] = None):
    """
    获取池化连接的上下文管理器
    
    Args:
        pool: 连接池实例
        timeout: 获取连接的超时时间
        
    Yields:
        Connection: 数据库连接对象
    """
    pooled_conn = None
    try:
        pooled_conn = pool.get_connection(timeout)
        yield pooled_conn.get_raw_connection()
    finally:
        if pooled_conn:
            pooled_conn.close()


if __name__ == "__main__":
    # 使用示例和测试代码
    print("=== 数据库连接池使用示例 ===")
    
    # 配置方式1：直接传入参数字典
    pool_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'password',
        'database': 'test_db',
        'max_connections': 5,
        'min_idle_connections': 2,
        'max_idle_connections': 3,
        'idle_timeout': 60
    }
    
    # 示例1：单例模式使用
    print("\n1. 单例模式使用示例:")
    print("-" * 50)
    
    try:
        # 首次创建单例实例
        pool1 = ConnectionPool.get_instance(pool_config)
        print(f"首次创建实例ID: {id(pool1)}")
        
        # 再次获取实例（应该是同一个）
        pool2 = ConnectionPool.get_instance()
        print(f"再次获取实例ID: {id(pool2)}")
        
        # 验证是否为同一实例
        print(f"是否为同一实例: {pool1 is pool2}")
        
        # 使用单例实例
        with pool1.get_connection() as pooled_conn:
            conn = pooled_conn.get_raw_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                print(f"查询结果: {result}")
        
        # 查看连接池状态
        status = pool1.get_pool_status()
        print(f"连接池状态: {status}")
        
    except ConnectionPoolError as e:
        print(f"连接池错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")
    
    # 示例2：便捷函数的单例模式
    print("\n2. 便捷函数单例模式示例:")
    print("-" * 50)
    
    try:
        # 重置单例（用于演示）
        ConnectionPool.reset_instance()
        
        # 使用便捷函数创建单例
        pool1 = create_connection_pool(pool_config, use_singleton=True)
        pool2 = create_connection_pool(use_singleton=True)  # 不传入配置，获取已存在的实例
        
        print(f"pool1 ID: {id(pool1)}")
        print(f"pool2 ID: {id(pool2)}")
        print(f"是否为同一实例: {pool1 is pool2}")
        
        # 检查单例状态
        print(f"单例是否已创建: {ConnectionPool.is_instance_created()}")
        
    except Exception as e:
        print(f"便捷函数单例模式错误: {e}")
    
    # 示例3：普通模式（非单例）
    print("\n3. 普通模式（非单例）示例:")
    print("-" * 50)
    
    try:
        # 创建两个独立的连接池实例
        pool1 = ConnectionPool(pool_config)
        pool2 = ConnectionPool(pool_config)
        
        print(f"pool1 ID: {id(pool1)}")
        print(f"pool2 ID: {id(pool2)}")
        print(f"是否为同一实例: {pool1 is pool2}")
        
        # 关闭连接池
        pool1.close()
        pool2.close()
        
    except Exception as e:
        print(f"普通模式错误: {e}")
    
    # 示例4：多线程单例模式
    print("\n4. 多线程单例模式示例:")
    print("-" * 50)
    
    import concurrent.futures
    import threading
    
    def worker_task(worker_id: int):
        """工作线程任务 - 获取单例实例"""
        try:
            # 每个线程都尝试获取单例实例
            pool = ConnectionPool.get_instance()
            print(f"工作线程 {worker_id}: 实例ID = {id(pool)}")
            
            with pool.get_connection() as pooled_conn:
                conn = pooled_conn.get_raw_connection()
                with conn.cursor() as cursor:
                    cursor.execute("SELECT CONNECTION_ID()")
                    conn_id = cursor.fetchone()
                    print(f"工作线程 {worker_id}: 连接ID = {conn_id}")
                    time.sleep(0.1)  # 模拟工作
                    return True
        except Exception as e:
            print(f"工作线程 {worker_id} 错误: {e}")
            return False
    
    try:
        # 重置单例（用于演示）
        ConnectionPool.reset_instance()
        
        # 首次创建单例
        pool = ConnectionPool.get_instance(pool_config)
        print(f"主线程创建实例ID: {id(pool)}")
        
        # 启动5个工作线程，都使用同一个单例
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker_task, i) for i in range(5)]
            
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
            print(f"多线程任务完成: {sum(results)}/{len(results)} 成功")
            
            # 查看最终状态
            final_status = pool.get_pool_status()
            print(f"最终连接池状态: {final_status}")
        
        # 关闭单例连接池
        pool.close()
        
    except Exception as e:
        print(f"多线程单例模式错误: {e}")
    
    print("\n=== 示例完成 ===")