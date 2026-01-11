#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连接池使用示例
演示如何配置和使用通用数据库连接池

@author: AI Assistant
@created: 2024-12-29
"""

import logging
import threading
import time
from mysql_tool import MySqlTool


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def basic_usage_example():
    """基础使用示例"""
    logger.info("=== 基础使用示例 ===")
    
    # 1. 初始化MySQL工具类，使用默认配置
    db_tool = MySqlTool(use_pool=True)
    
    # 2. 获取连接池状态
    pool_status = db_tool.get_pool_status()
    logger.info(f"连接池初始状态: {pool_status}")
    
    # 3. 使用连接池执行查询
    try:
        with db_tool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                result = cursor.fetchone()
                logger.info(f"MySQL版本: {result['VERSION()']}")
                
                # 获取表列表
                tables = db_tool.get_tables()
                logger.info(f"数据库中的表: {tables}")
    except Exception as e:
        logger.error(f"执行查询失败: {str(e)}")
    
    # 4. 再次获取连接池状态
    pool_status = db_tool.get_pool_status()
    logger.info(f"连接池状态: {pool_status}")
    
    # 5. 关闭连接池
    db_tool.close()


def custom_pool_config_example():
    """自定义连接池配置示例"""
    logger.info("\n=== 自定义连接池配置示例 ===")
    
    # 自定义连接池配置
    pool_config = {
        'max_connections': 15,
        'min_idle_connections': 3,
        'max_idle_connections': 5,
        'idle_timeout': 600,
        'connect_timeout': 15,
        'retry_times': 5,
        'blocking': True,
        'wait_timeout': 30
    }
    
    # 初始化MySQL工具类，使用自定义连接池配置
    db_tool = MySqlTool(use_pool=True, pool_config=pool_config)
    
    # 获取连接池状态
    pool_status = db_tool.get_pool_status()
    logger.info(f"连接池初始状态: {pool_status}")
    
    # 使用连接
    try:
        with db_tool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT DATABASE()")
                result = cursor.fetchone()
                logger.info(f"当前数据库: {result['DATABASE()']}")
    except Exception as e:
        logger.error(f"执行查询失败: {str(e)}")
    
    db_tool.close()


def concurrent_usage_example():
    """并发使用示例"""
    logger.info("\n=== 并发使用示例 ===")
    
    # 初始化MySQL工具类，使用较小的连接池配置以测试并发控制
    pool_config = {
        'max_connections': 5,
        'min_idle_connections': 2,
        'max_idle_connections': 3,
        'blocking': True,
        'wait_timeout': 10
    }
    db_tool = MySqlTool(use_pool=True, pool_config=pool_config)
    
    # 定义并发任务
    def concurrent_task(task_id):
        try:
            logger.info(f"任务 {task_id}: 开始执行")
            
            # 获取连接并执行查询
            with db_tool.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 模拟耗时操作
                    time.sleep(2)
                    cursor.execute("SELECT CONNECTION_ID()")
                    result = cursor.fetchone()
                    conn_id = result['CONNECTION_ID()']
                    
                    # 获取当前连接池状态
                    pool_status = db_tool.get_pool_status()
                    logger.info(f"任务 {task_id}: 完成，连接ID: {conn_id}, 连接池状态: {pool_status}")
                    
        except Exception as e:
            logger.error(f"任务 {task_id}: 执行失败 - {str(e)}")
    
    # 启动10个并发任务（超过最大连接数5个）
    threads = []
    for i in range(10):
        thread = threading.Thread(target=concurrent_task, args=(i,))
        threads.append(thread)
        thread.start()
    
    # 等待所有任务完成
    for thread in threads:
        thread.join()
    
    # 最终连接池状态
    pool_status = db_tool.get_pool_status()
    logger.info(f"并发任务完成后连接池状态: {pool_status}")
    
    db_tool.close()


def exception_handling_example():
    """异常处理示例"""
    logger.info("\n=== 异常处理示例 ===")
    
    # 初始化MySQL工具类，使用较小的连接池配置
    pool_config = {
        'max_connections': 2,
        'min_idle_connections': 1,
        'blocking': False  # 不阻塞，连接耗尽时直接抛出异常
    }
    db_tool = MySqlTool(use_pool=True, pool_config=pool_config)
    
    try:
        # 获取两个连接（达到最大连接数）
        conn1 = db_tool.get_connection()
        conn2 = db_tool.get_connection()
        
        # 获取第三个连接，应该抛出异常
        conn3 = db_tool.get_connection()
        logger.info("错误：应该抛出连接耗尽异常")
        
    except Exception as e:
        logger.info(f"捕获到预期异常: {type(e).__name__} - {str(e)}")
    
    finally:
        # 释放连接
        if 'conn1' in locals():
            db_tool._pool.release_connection(conn1)
        if 'conn2' in locals():
            db_tool._pool.release_connection(conn2)
        if 'conn3' in locals():
            db_tool._pool.release_connection(conn3)
        
        db_tool.close()


def context_manager_example():
    """上下文管理器使用示例"""
    logger.info("\n=== 上下文管理器使用示例 ===")
    
    # 使用上下文管理器自动管理连接池
    pool_config = {
        'max_connections': 5,
        'min_idle_connections': 2
    }
    
    with MySqlTool(use_pool=True, pool_config=pool_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 + 1")
            result = cursor.fetchone()
            logger.info(f"计算结果: {result['1 + 1']}")
    
    # 连接池会自动关闭


def insert_and_query_example():
    """插入和查询示例"""
    logger.info("\n=== 插入和查询示例 ===")
    
    db_tool = MySqlTool(use_pool=True)
    
    try:
        # 插入数据
        with db_tool.get_connection() as conn:
            with conn.cursor() as cursor:
                # 创建测试表
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS test_table (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    value INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
                cursor.execute(create_table_sql)
                logger.info("测试表已创建")
                
                # 插入数据
                insert_sql = "INSERT INTO test_table (name, value) VALUES (%s, %s)"
                cursor.execute(insert_sql, ("测试数据1", 100))
                cursor.execute(insert_sql, ("测试数据2", 200))
                logger.info("数据插入成功")
        
        # 查询数据
        with db_tool.get_connection() as conn:
            with conn.cursor() as cursor:
                select_sql = "SELECT * FROM test_table ORDER BY id"
                cursor.execute(select_sql)
                results = cursor.fetchall()
                logger.info(f"查询结果: {results}")
                
                # 统计数据
                count_sql = "SELECT COUNT(*) FROM test_table"
                cursor.execute(count_sql)
                count = cursor.fetchone()
                logger.info(f"数据总数: {count['COUNT(*)']}")
        
        # 删除测试表
        with db_tool.get_connection() as conn:
            with conn.cursor() as cursor:
                drop_table_sql = "DROP TABLE IF EXISTS test_table"
                cursor.execute(drop_table_sql)
                logger.info("测试表已删除")
                
    except Exception as e:
        logger.error(f"执行操作失败: {str(e)}")
    
    finally:
        db_tool.close()


if __name__ == "__main__":
    # 运行所有示例
    basic_usage_example()
    custom_pool_config_example()
    concurrent_usage_example()
    exception_handling_example()
    context_manager_example()
    insert_and_query_example()
