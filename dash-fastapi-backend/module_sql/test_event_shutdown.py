#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试连接池健康检查线程的即时退出功能
使用Event实现，确保调用close方法时健康检查线程能够立即退出
"""

import time
import logging
from unittest.mock import patch
from connection_pool import ConnectionPool

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_event_shutdown():
    """测试健康检查线程的即时退出功能"""
    print("=== 测试健康检查线程即时退出功能 ===")
    
    # 使用mock来模拟数据库连接创建，避免实际连接数据库
    with patch('connection_pool.pymysql.connect') as mock_connect:
        # 配置mock返回值
        mock_conn = mock_connect.return_value
        mock_conn.open = True
        mock_conn.ping.return_value = None
        
        try:
            # 创建连接池，设置较长的健康检查间隔以便测试即时退出
            pool = ConnectionPool(
                host='localhost',
                port=3306,  # 添加端口参数
                user='test',
                password='test',
                database='test_db',
                health_check_interval=30  # 设置30秒的健康检查间隔
            )
            
            print("连接池创建成功（使用mock）")
            print("健康检查线程已启动，设置了30秒的检查间隔")
            
            # 稍微等待一下，确保健康检查线程已经开始运行
            time.sleep(1)
            
            # 记录关闭开始时间
            start_time = time.time()
            
            print("开始关闭连接池...")
            print("健康检查线程应该立即收到关闭信号并退出（而不是等待30秒）")
            
            # 调用close方法，测试是否能快速关闭
            pool.close()
            
            # 计算关闭耗时
            close_time = time.time() - start_time
            
            print(f"连接池关闭完成，耗时: {close_time:.3f} 秒")
            print(f"健康检查间隔设置为30秒，如果关闭耗时远小于这个值，说明即时退出功能正常")
            
            # 验证关闭是否成功
            if close_time < 2:  # 如果关闭时间小于2秒，认为即时退出功能正常
                print("✅ 测试通过: 健康检查线程实现了即时退出")
            else:
                print("❌ 测试失败: 健康检查线程可能没有及时退出")
                
        except Exception as e:
            print(f"测试过程中出现异常: {e}")
        finally:
            # 确保重置单例
            ConnectionPool.reset_instance()

def test_without_event_comparison():
    """对比测试：说明没有Event时的行为 vs 有Event时的行为"""
    print("\n=== 对比测试说明 ===")
    print("在优化前（使用time.sleep）：")
    print("- 当调用close()方法时，健康检查线程会继续睡眠直到health_check_interval超时")
    print("- 这可能导致连接池关闭延迟，特别是当health_check_interval设置较大时")
    print("- 例如：如果health_check_interval=30秒，关闭可能需要等待接近30秒")
    print("\n优化后（使用Event）：")
    print("- 当调用close()方法时，会立即设置_shutdown_event，唤醒健康检查线程")
    print("- 健康检查线程检测到事件后会立即退出循环，无需等待睡眠结束")
    print("- 连接池可以在毫秒级别完成关闭，不受health_check_interval影响")
    print("- 这提高了资源释放效率，特别是在应用程序关闭时")

if __name__ == "__main__":
    # 运行测试
    test_event_shutdown()
    test_without_event_comparison()
    print("\n=== 测试完成 ===")

