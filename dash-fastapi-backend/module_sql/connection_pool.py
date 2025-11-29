#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用数据库连接池模块
兼容Python 3.8+
支持MySQL数据库，预留其他数据库扩展接口

核心功能：连接复用、并发控制、资源自动释放

@author: AI Assistant
@created: 2024-12-29
"""

import os
import logging
import threading
import time
from typing import Dict, List, Optional, Union, Any, Tuple
from contextlib import contextmanager
import pymysql
from pymysql.connections import Connection
from pymysql.err import OperationalError, ProgrammingError, IntegrityError


class ConnectionPoolError(Exception):
    """连接池异常基类"""
    pass


class ConnectionTimeoutError(ConnectionPoolError):
    """连接超时异常"""
    pass


class ConnectionExhaustedError(ConnectionPoolError):
    """连接耗尽异常"""
    pass


class InvalidConnectionError(ConnectionPoolError):
    """无效连接异常"""
    pass


class ConnectionPool:
    """通用数据库连接池类"""

    def __init__(
        self,
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
    ):
        """
        初始化连接池

        Args:
            config: 数据库连接配置
                必选参数：host, user, password, database
                可选参数：port, charset, autocommit, cursorclass, connect_timeout
            max_connections: 最大连接数（默认10，最小1）
            min_idle_connections: 最小空闲连接数（默认2，启动时预创建）
            max_idle_connections: 最大空闲连接数（默认5，超出部分自动关闭）
            idle_timeout: 空闲连接超时时间（默认300秒，超时自动关闭）
            connect_timeout: 连接数据库超时时间（默认10秒）
            retry_times: 连接失败自动重试次数（默认3次）
            blocking: 无可用连接时是否阻塞等待（默认True）
            wait_timeout: 阻塞等待超时时间（默认60秒，仅blocking=True时生效）
            logger: 日志对象，若为None则创建默认日志对象
        """
        # 验证参数
        self._validate_parameters(
            max_connections, min_idle_connections, max_idle_connections,
            idle_timeout, connect_timeout, retry_times, wait_timeout
        )

        # 配置参数
        self.config = config.copy()
        self.max_connections = max_connections
        self.min_idle_connections = min_idle_connections
        self.max_idle_connections = max_idle_connections
        self.idle_timeout = idle_timeout
        self.connect_timeout = connect_timeout
        self.retry_times = retry_times
        self.blocking = blocking
        self.wait_timeout = wait_timeout

        # 日志配置
        self.logger = logger or self._setup_default_logger()

        # 连接池状态
        self._connections: List[Dict[str, Any]] = []  # 存储连接信息：{'conn': Connection, 'last_used': float}
        self._active_count = 0  # 活跃连接数
        self._wait_queue = []  # 等待连接的线程队列
        self._closed = False  # 连接池是否已关闭

        # 线程同步
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)

        # 初始化空闲连接
        self._initialize_idle_connections()

        # 启动空闲连接清理线程
        self._start_cleanup_thread()

        self.logger.info(f"连接池初始化完成 - Max: {max_connections}, Min idle: {min_idle_connections}")

    def _validate_parameters(
        self,
        max_connections: int,
        min_idle_connections: int,
        max_idle_connections: int,
        idle_timeout: int,
        connect_timeout: int,
        retry_times: int,
        wait_timeout: int
    ):
        """验证参数合法性"""
        if max_connections < 1:
            raise ConnectionPoolError("max_connections 必须大于等于1")
        if min_idle_connections < 0:
            raise ConnectionPoolError("min_idle_connections 必须大于等于0")
        if max_idle_connections < min_idle_connections:
            raise ConnectionPoolError("max_idle_connections 必须大于等于min_idle_connections")
        if max_connections < min_idle_connections:
            raise ConnectionPoolError("max_connections 必须大于等于min_idle_connections")
        if idle_timeout < 1:
            raise ConnectionPoolError("idle_timeout 必须大于等于1秒")
        if connect_timeout < 1:
            raise ConnectionPoolError("connect_timeout 必须大于等于1秒")
        if retry_times < 0:
            raise ConnectionPoolError("retry_times 必须大于等于0")
        if wait_timeout < 1:
            raise ConnectionPoolError("wait_timeout 必须大于等于1秒")

    def _setup_default_logger(self) -> logging.Logger:
        """设置默认日志配置"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _initialize_idle_connections(self):
        """初始化最小空闲连接数"""
        try:
            with self._lock:
                for _ in range(self.min_idle_connections):
                    if self._closed:
                        break
                    if len(self._connections) < self.max_connections:
                        conn = self._create_connection()
                        if conn:
                            self._connections.append({'conn': conn, 'last_used': time.time()})
        except Exception as e:
            self.logger.error(f"初始化空闲连接失败: {str(e)}")

    def _start_cleanup_thread(self):
        """启动空闲连接清理线程"""
        def cleanup_idle_connections():
            while not self._closed:
                try:
                    with self._lock:
                        now = time.time()
                        # 清理超时的空闲连接
                        to_remove = []
                        for i, conn_info in enumerate(self._connections):
                            if now - conn_info['last_used'] > self.idle_timeout:
                                to_remove.append(i)

                        # 关闭并移除超时连接
                        for i in reversed(to_remove):
                            conn_info = self._connections.pop(i)
                            try:
                                conn_info['conn'].close()
                                self.logger.debug(f"空闲连接超时，已关闭: {conn_info['conn']}")
                            except Exception as e:
                                self.logger.error(f"关闭超时连接失败: {str(e)}")

                        # 确保空闲连接数不超过max_idle_connections
                        while len(self._connections) > self.max_idle_connections:
                            conn_info = self._connections.pop(0)
                            try:
                                conn_info['conn'].close()
                                self.logger.debug(f"空闲连接数超过最大值，已关闭: {conn_info['conn']}")
                            except Exception as e:
                                self.logger.error(f"关闭超额空闲连接失败: {str(e)}")

                    # 每隔30秒检查一次
                    time.sleep(30)
                except Exception as e:
                    self.logger.error(f"清理空闲连接线程出错: {str(e)}")
                    time.sleep(30)

        # 启动后台线程
        self._cleanup_thread = threading.Thread(target=cleanup_idle_connections, daemon=True)
        self._cleanup_thread.start()

    def _create_connection(self) -> Optional[Connection]:
        """
        创建数据库连接（钩子方法，可重写以支持其他数据库）

        Returns:
            Connection: 数据库连接对象，失败则返回None
        """
        try:
            # 准备连接参数
            conn_params = {
                'host': self.config.get('host'),
                'user': self.config.get('user'),
                'password': self.config.get('password'),
                'database': self.config.get('database'),
                'port': self.config.get('port', 3306),
                'charset': self.config.get('charset', 'utf8mb4'),
                'autocommit': self.config.get('autocommit', True),
                'connect_timeout': self.connect_timeout
            }

            # 可选参数
            if 'cursorclass' in self.config:
                conn_params['cursorclass'] = self.config['cursorclass']

            # 尝试连接
            for attempt in range(self.retry_times + 1):
                try:
                    conn = pymysql.connect(**conn_params)
                    self.logger.debug(f"成功创建数据库连接 (尝试 {attempt + 1}/{self.retry_times + 1})")
                    return conn
                except OperationalError as e:
                    self.logger.warning(f"创建数据库连接失败 (尝试 {attempt + 1}/{self.retry_times + 1}): {str(e)}")
                    if attempt < self.retry_times:
                        time.sleep(1)  # 重试间隔1秒

            self.logger.error(f"创建数据库连接失败，已尝试{self.retry_times + 1}次")
            return None

        except Exception as e:
            self.logger.error(f"创建数据库连接时发生未知错误: {str(e)}")
            return None

    def _validate_connection(self, conn: Connection) -> bool:
        """
        验证连接有效性（钩子方法，可重写以支持其他数据库）

        Args:
            conn: 数据库连接对象

        Returns:
            bool: 连接是否有效
        """
        try:
            conn.ping(reconnect=False)  # 不自动重连，由连接池管理
            return True
        except Exception as e:
            self.logger.debug(f"连接验证失败: {str(e)}")
            return False

    def get_connection(self) -> Connection:
        """
        获取数据库连接

        Returns:
            Connection: 数据库连接对象

        Raises:
            ConnectionExhaustedError: 连接耗尽且不阻塞时
            ConnectionTimeoutError: 阻塞等待超时
            InvalidConnectionError: 无法创建有效连接
        """
        if self._closed:
            raise ConnectionPoolError("连接池已关闭")

        with self._lock:
            # 先尝试从空闲连接中获取
            while self._connections:
                conn_info = self._connections.pop(0)
                conn = conn_info['conn']

                if self._validate_connection(conn):
                    self._active_count += 1
                    self.logger.debug(f"从连接池获取到空闲连接: {conn}")
                    return conn
                else:
                    # 连接无效，关闭并尝试下一个
                    try:
                        conn.close()
                        self.logger.debug(f"无效连接已关闭: {conn}")
                    except Exception as e:
                        self.logger.error(f"关闭无效连接失败: {str(e)}")

            # 空闲连接已耗尽，尝试创建新连接
            if self._active_count < self.max_connections:
                conn = self._create_connection()
                if conn:
                    self._active_count += 1
                    self.logger.debug(f"创建新的数据库连接: {conn}")
                    return conn

            # 无法创建新连接，处理阻塞等待逻辑
            if not self.blocking:
                raise ConnectionExhaustedError(
                    f"连接池已耗尽，当前活跃连接数: {self._active_count}, 最大连接数: {self.max_connections}"
                )

            # 添加到等待队列
            wait_event = threading.Event()
            self._wait_queue.append(wait_event)
            self.logger.debug(f"连接池已耗尽，添加到等待队列 (活跃数: {self._active_count}, 等待队列长度: {len(self._wait_queue)})")
            
            wait_start = time.time()
            try:
                while True:
                    # 检查等待是否超时
                    if time.time() - wait_start > self.wait_timeout:
                        raise ConnectionTimeoutError(
                            f"获取连接超时，已等待{self.wait_timeout}秒，当前活跃连接数: {self._active_count}"
                        )

                    # 等待连接可用
                    if not wait_event.wait(timeout=1):
                        continue

                    # 再次尝试获取连接
                    while self._connections:
                        conn_info = self._connections.pop(0)
                        conn = conn_info['conn']

                        if self._validate_connection(conn):
                            self._active_count += 1
                            self.logger.debug(f"从连接池获取到空闲连接（等待后）: {conn}")
                            return conn
                        else:
                            # 连接无效，关闭并尝试下一个
                            try:
                                conn.close()
                                self.logger.debug(f"无效连接已关闭（等待后）: {conn}")
                            except Exception as e:
                                self.logger.error(f"关闭无效连接失败（等待后）: {str(e)}")

                    # 尝试创建新连接
                    if self._active_count < self.max_connections:
                        conn = self._create_connection()
                        if conn:
                            self._active_count += 1
                            self.logger.debug(f"创建新的数据库连接（等待后）: {conn}")
                            return conn
            finally:
                # 从等待队列中移除
                if wait_event in self._wait_queue:
                    self._wait_queue.remove(wait_event)

    def release_connection(self, conn: Connection) -> None:
        """
        释放数据库连接（归还到连接池）

        Args:
            conn: 数据库连接对象
        """
        if self._closed:
            try:
                conn.close()
                self.logger.debug(f"连接池已关闭，直接关闭连接: {conn}")
            except Exception as e:
                self.logger.error(f"关闭连接失败: {str(e)}")
            return

        with self._lock:
            if self._active_count <= 0:
                self.logger.warning("尝试释放不存在的活跃连接")
                return

            # 减少活跃连接数
            self._active_count -= 1

            # 验证连接是否仍然有效
            if self._validate_connection(conn):
                # 归还到连接池
                if len(self._connections) < self.max_idle_connections:
                    self._connections.append({'conn': conn, 'last_used': time.time()})
                    self.logger.debug(f"连接已归还到连接池: {conn}")
                    # 通知等待队列中的第一个线程
                    if self._wait_queue:
                        wait_event = self._wait_queue.pop(0)
                        wait_event.set()
                else:
                    # 空闲连接数已达上限，直接关闭
                    try:
                        conn.close()
                        self.logger.debug(f"空闲连接数已达上限，关闭连接: {conn}")
                    except Exception as e:
                        self.logger.error(f"关闭连接失败: {str(e)}")
            else:
                # 连接无效，直接关闭
                try:
                    conn.close()
                    self.logger.debug(f"无效连接已关闭: {conn}")
                except Exception as e:
                    self.logger.error(f"关闭无效连接失败: {str(e)}")

            # 如果空闲连接数不足，尝试补充
            while len(self._connections) < self.min_idle_connections and \
                    (len(self._connections) + self._active_count) < self.max_connections:
                conn = self._create_connection()
                if conn:
                    self._connections.append({'conn': conn, 'last_used': time.time()})
                    self.logger.debug(f"补充空闲连接: {conn}")
                    # 通知等待队列中的第一个线程
                    if self._wait_queue:
                        wait_event = self._wait_queue.pop(0)
                        wait_event.set()
                else:
                    break

    def close(self) -> None:
        """关闭连接池，释放所有资源"""
        if self._closed:
            return

        with self._lock:
            self._closed = True
            
            # 唤醒所有等待的线程并清空等待队列
            for wait_event in self._wait_queue:
                wait_event.set()
            self._wait_queue.clear()

            # 关闭所有空闲连接
            for conn_info in self._connections:
                try:
                    conn_info['conn'].close()
                    self.logger.debug(f"关闭空闲连接: {conn_info['conn']}")
                except Exception as e:
                    self.logger.error(f"关闭空闲连接失败: {str(e)}")
            self._connections.clear()

            self.logger.info("连接池已关闭，所有空闲连接已释放。活跃连接将在使用者释放时自动关闭。")

    def get_pool_status(self) -> Dict[str, int]:
        """
        获取连接池当前状态

        Returns:
            Dict: 连接池状态信息，包含：
                - total_connections: 总连接数（活跃+空闲）
                - active_connections: 活跃连接数
                - idle_connections: 空闲连接数
                - wait_queue_length: 等待队列长度
        """
        with self._lock:
            return {
                'total_connections': self._active_count + len(self._connections),
                'active_connections': self._active_count,
                'idle_connections': len(self._connections),
                'wait_queue_length': len(self._wait_queue)
            }

    @contextmanager
    def connection(self):
        """
        数据库连接上下文管理器

        Example:
            with pool.connection() as conn:
                # 使用连接执行操作
                pass
        """
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        finally:
            if conn:
                self.release_connection(conn)

    def __del__(self):
        """析构函数，确保连接池关闭"""
        self.close()


# 连接池单例装饰器
def singleton(cls):
    """单例装饰器"""
    instances = {}
    lock = threading.Lock()

    def get_instance(*args, **kwargs):
        with lock:
            if cls not in instances:
                instances[cls] = cls(*args, **kwargs)
            return instances[cls]

    return get_instance
