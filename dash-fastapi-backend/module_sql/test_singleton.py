#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连接池单例模式测试脚本
"""

import threading
import time
from mysql_tool import MySqlTool
from connection_pool import ConnectionPool


def test_connection_pool_singleton():
    """测试连接池单例模式"""
    print("=== 连接池单例模式测试 ===\n")
    
    # 测试1: 基本单例功能
    print("1. 基本单例功能测试:")
    try:
        # 重置单例
        ConnectionPool.reset_instance()
        
        # 创建第一个实例
        pool1 = ConnectionPool.get_instance({
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'password',
            'database': 'test_db',
            'max_connections': 5
        })
        
        # 创建第二个实例
        pool2 = ConnectionPool.get_instance()
        
        print(f"   pool1 ID: {id(pool1)}")
        print(f"   pool2 ID: {id(pool2)}")
        print(f"   是否为同一实例: {pool1 is pool2}")
        print(f"   单例是否已创建: {ConnectionPool.is_instance_created()}")
        
        # 关闭单例
        pool1.close()
        
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试2: MySqlTool集成单例模式
    print("\n2. MySqlTool集成单例模式测试:")
    try:
        # 重置单例
        ConnectionPool.reset_instance()
        
        # 创建两个MySqlTool实例，都使用单例模式
        db_tool1 = MySqlTool(use_pool_singleton=True)
        db_tool2 = MySqlTool(use_pool_singleton=True)
        
        print(f"   db_tool1的连接池实例ID: {id(db_tool1._pool_instance)}")
        print(f"   db_tool2的连接池实例ID: {id(db_tool2._pool_instance)}")
        print(f"   是否为同一连接池实例: {db_tool1._pool_instance is db_tool2._pool_instance}")
        
        # 关闭连接池
        db_tool1.close_pool()
        
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试3: 多线程环境下的单例
    print("\n3. 多线程环境下的单例测试:")
    
    results = []
    
    def worker(thread_id):
        try:
            # 每个线程都尝试获取单例实例
            pool = ConnectionPool.get_instance()
            results.append({
                'thread_id': thread_id,
                'pool_id': id(pool),
                'success': True
            })
            print(f"   线程{thread_id}: 成功获取单例实例，ID={id(pool)}")
        except Exception as e:
            results.append({
                'thread_id': thread_id,
                'pool_id': None,
                'success': False,
                'error': str(e)
            })
            print(f"   线程{thread_id}: 错误 - {e}")
    
    try:
        # 重置单例
        ConnectionPool.reset_instance()
        
        # 首次创建单例
        pool = ConnectionPool.get_instance({
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'password',
            'database': 'test_db',
            'max_connections': 10
        })
        
        # 启动多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        success_count = sum(1 for r in results if r['success'])
        pool_ids = [r['pool_id'] for r in results if r['success']]
        unique_ids = set(pool_ids)
        
        print(f"   成功线程数: {success_count}/{len(results)}")
        print(f"   唯一实例ID数: {len(unique_ids)}")
        print(f"   是否都指向同一实例: {len(unique_ids) == 1}")
        
        # 关闭单例
        pool.close()
        
    except Exception as e:
        print(f"   错误: {e}")
    
    # 测试4: 单例重置功能
    print("\n4. 单例重置功能测试:")
    try:
        # 创建单例
        pool1 = ConnectionPool.get_instance({
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'password',
            'database': 'test_db',
            'max_connections': 5
        })
        
        print(f"   重置前实例ID: {id(pool1)}")
        print(f"   重置前单例状态: {ConnectionPool.is_instance_created()}")
        
        # 重置单例
        ConnectionPool.reset_instance()
        
        print(f"   重置后单例状态: {ConnectionPool.is_instance_created()}")
        
        # 再次创建单例
        pool2 = ConnectionPool.get_instance({
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'password',
            'database': 'test_db',
            'max_connections': 5
        })
        
        print(f"   新实例ID: {id(pool2)}")
        print(f"   是否为不同实例: {pool1 is not pool2}")
        
        # 关闭新单例
        pool2.close()
        
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n=== 单例模式测试完成 ===")


if __name__ == "__main__":
    test_connection_pool_singleton()