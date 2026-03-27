#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL工具类使用示例
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mysql_tool import MySqlTool


def basic_usage_example():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    try:
        # 创建数据库工具类实例（使用默认配置文件）
        db = MySqlTool()
        
        # 获取数据库中的所有表
        tables = db.get_tables()
        print(f"数据库中的表: {tables}")
        
        # 查看表结构
        if tables:
            print(f"\n表 {tables[0]} 的结构:")
            db.print_table_structure(tables[0])
        
    except Exception as e:
        print(f"错误: {e}")


def table_creation_example():
    """表创建示例"""
    print("\n=== 表创建示例 ===")
    
    try:
        db = MySqlTool()
        
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
            },
            {
                'name': 'age',
                'type': 'INT',
                'nullable': True,
                'default': 0,
                'comment': '年龄'
            },
            {
                'name': 'created_at',
                'type': 'DATETIME',
                'nullable': False,
                'default': 'CURRENT_TIMESTAMP',
                'comment': '创建时间'
            }
        ]
        
        # 创建表
        success = db.create_table('users', fields, drop_if_exists=True)
        if success:
            print("表 'users' 创建成功")
            db.print_table_structure('users')
        else:
            print("表创建失败")
            
    except Exception as e:
        print(f"错误: {e}")


def sql_execution_example():
    """SQL执行示例"""
    print("\n=== SQL执行示例 ===")
    
    try:
        db = MySqlTool()
        
        # 插入数据
        insert_sql = "INSERT INTO users (username, email, age) VALUES (%s, %s, %s)"
        insert_params = ('test_user', 'test@example.com', 25)
        
        affected_rows = db.execute_sql(insert_sql, insert_params)
        print(f"插入数据成功，影响行数: {affected_rows}")
        
        # 查询数据
        select_sql = "SELECT * FROM users WHERE username = %s"
        results = db.execute_sql(select_sql, ('test_user',))
        print(f"查询结果: {results}")
        
        # 更新数据
        update_sql = "UPDATE users SET age = %s WHERE username = %s"
        affected_rows = db.execute_sql(update_sql, (26, 'test_user'))
        print(f"更新数据成功，影响行数: {affected_rows}")
        
        # 删除数据
        delete_sql = "DELETE FROM users WHERE username = %s"
        affected_rows = db.execute_sql(delete_sql, ('test_user',))
        print(f"删除数据成功，影响行数: {affected_rows}")
        
    except Exception as e:
        print(f"错误: {e}")


def transaction_example():
    """事务处理示例"""
    print("\n=== 事务处理示例 ===")
    
    try:
        db = MySqlTool()
        
        # 使用上下文管理器自动处理事务
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    # 开始事务
                    conn.begin()
                    
                    # 执行多个操作
                    cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", 
                                 ('user1', 'user1@example.com'))
                    cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", 
                                 ('user2', 'user2@example.com'))
                    
                    # 提交事务
                    conn.commit()
                    print("事务提交成功")
                    
                except Exception as e:
                    # 回滚事务
                    conn.rollback()
                    print(f"事务回滚: {e}")
                    
    except Exception as e:
        print(f"错误: {e}")


def sql_file_example():
    """SQL文件执行示例"""
    print("\n=== SQL文件执行示例 ===")
    
    # 创建示例SQL文件
    sql_content = """
-- 创建测试表
CREATE TABLE IF NOT EXISTS test_table (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    value INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 插入测试数据
INSERT INTO test_table (name, value) VALUES ('测试1', 100);
INSERT INTO test_table (name, value) VALUES ('测试2', 200);

-- 查询数据
SELECT * FROM test_table;
"""
    
    # 写入临时SQL文件
    sql_file_path = 'temp_test.sql'
    with open(sql_file_path, 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    try:
        db = MySqlTool()
        
        # 执行SQL文件
        result = db.execute_sql_file(sql_file_path, continue_on_error=True)
        
        print(f"SQL文件执行结果:")
        print(f"总语句数: {result['total']}")
        print(f"成功: {result['success']}")
        print(f"失败: {result['failed']}")
        
        if result['errors']:
            print("错误详情:")
            for error in result['errors']:
                print(f"  语句{error['statement_index']}: {error['error']}")
        
        # 验证执行结果
        results = db.execute_sql("SELECT * FROM test_table")
        print(f"查询结果: {results}")
        
        # 清理测试表
        db.execute_sql("DROP TABLE IF EXISTS test_table")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        # 删除临时文件
        if os.path.exists(sql_file_path):
            os.remove(sql_file_path)


def custom_config_example():
    """自定义配置示例"""
    print("\n=== 自定义配置示例 ===")
    
    try:
        # 使用自定义配置文件路径
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        db = MySqlTool(config_path=config_path)
        
        # 获取表列表
        tables = db.get_tables()
        print(f"使用自定义配置，数据库中的表: {tables}")
        
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    # 运行所有示例
    basic_usage_example()
    table_creation_example()
    sql_execution_example()
    transaction_example()
    sql_file_example()
    custom_config_example()
    
    print("\n=== 所有示例执行完成 ===")
    print("请根据实际需求修改配置文件中的数据库连接信息")