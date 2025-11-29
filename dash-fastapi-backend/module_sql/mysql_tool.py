#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL数据库操作工具类
兼容Python 3.8+
依赖：pymysql, configparser
安装：pip install pymysql

@author: AI Assistant
@created: 2024-12-29
@updated: 2024-12-29 - 集成通用连接池功能
"""

import os
import re
import logging
import configparser
from typing import Dict, List, Optional, Union, Any, Tuple
from contextlib import contextmanager
import pymysql
from pymysql.connections import Connection
from pymysql.cursors import DictCursor
from pymysql.err import OperationalError, ProgrammingError, IntegrityError

# 导入连接池模块
from connection_pool import ConnectionPool, ConnectionPoolError, get_pooled_connection


class MySqlTool:
    """MySQL数据库操作工具类 - 集成通用连接池功能"""
    
    def __init__(self, config_path: Optional[str] = None, use_pool: bool = True, pool_config: Optional[Dict[str, Any]] = None, use_pool_singleton: bool = False):
        """
        初始化MySQL工具类
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
            use_pool: 是否使用连接池
            pool_config: 连接池配置参数，如果为None则使用默认配置
            use_pool_singleton: 是否使用连接池单例模式（仅在use_pool=True时有效）
        """
        self.config_path = config_path or self._get_default_config_path()
        self.use_pool = use_pool
        self.pool_config = pool_config or {}
        self.use_pool_singleton = use_pool_singleton
        self.config = {}
        self.connection = None
        self.logger = self._setup_logger()
        
        # 加载配置
        self._load_config()
        
        # 连接池相关
        self._pool = None
        self._pool_instance = None
        if use_pool:
            self._init_pool()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志配置"""
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
    
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        # 获取当前module_sql目录路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 优先在当前目录查找配置文件，其次查找项目根目录
        config_ini_path = os.path.join(current_dir, 'config.ini')
        env_path = os.path.join(current_dir, '.env')
        
        if os.path.exists(config_ini_path):
            return config_ini_path
        elif os.path.exists(env_path):
            return env_path
        else:
            # 如果当前目录没有，则查找项目根目录
            project_root = os.path.dirname(os.path.dirname(current_dir))
            project_config_ini = os.path.join(project_root, 'config.ini')
            project_env = os.path.join(project_root, '.env')
            
            if os.path.exists(project_config_ini):
                return project_config_ini
            elif os.path.exists(project_env):
                return project_env
            else:
                return config_ini_path  # 默认返回当前目录的ini路径
    
    def _load_config(self) -> None:
        """加载数据库配置"""
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
            
            if self.config_path.endswith('.ini'):
                self._load_ini_config()
            elif self.config_path.endswith('.env'):
                self._load_env_config()
            else:
                raise ValueError(f"不支持的配置文件格式: {self.config_path}")
            
            # 验证必要参数
            required_params = ['host', 'user', 'password', 'database']
            missing_params = [param for param in required_params if not self.config.get(param)]
            if missing_params:
                raise ValueError(f"配置文件中缺少必要参数: {missing_params}")
            
            self.logger.info(f"配置加载成功: {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"配置文件加载失败: {str(e)}")
            raise
    
    def _load_ini_config(self) -> None:
        """加载INI配置文件"""
        config = configparser.ConfigParser()
        config.read(self.config_path, encoding='utf-8')
        
        # 支持[mysql]或[database]或[db]section
        sections = ['mysql', 'database', 'db']
        target_section = None
        
        for section in sections:
            if section in config.sections():
                target_section = section
                break
        
        if not target_section:
            raise ValueError(f"INI文件中未找到有效的section: {sections}")
        
        section_config = config[target_section]
        self.config = {
            'host': section_config.get('host', 'localhost'),
            'port': int(section_config.get('port', '3306')),
            'user': section_config.get('user'),
            'password': section_config.get('password'),
            'database': section_config.get('database'),
            'charset': section_config.get('charset', 'utf8mb4'),
            'connect_timeout': int(section_config.get('connect_timeout', '30')),
            'autocommit': section_config.getboolean('autocommit', True)
        }
    
    def _load_env_config(self) -> None:
        """加载环境变量配置文件"""
        from dotenv import load_dotenv
        load_dotenv(self.config_path)
        
        self.config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', '3306')),
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DATABASE'),
            'charset': os.getenv('MYSQL_CHARSET', 'utf8mb4'),
            'connect_timeout': int(os.getenv('MYSQL_CONNECT_TIMEOUT', '30')),
            'autocommit': os.getenv('MYSQL_AUTOCOMMIT', 'true').lower() == 'true'
        }
    
    def _init_pool(self) -> None:
        """初始化连接池 - 使用通用连接池类"""
        try:
            # 构建连接池配置
            pool_config = {
                'host': self.config['host'],
                'port': self.config['port'],
                'user': self.config['user'],
                'password': self.config['password'],
                'database': self.config['database'],
                'charset': self.config['charset'],
                'cursorclass': DictCursor,
                'autocommit': self.config['autocommit'],
                'connect_timeout': self.config['connect_timeout']
            }
            
            # 合并用户提供的连接池配置
            pool_config.update(self.pool_config)
            
            # 根据是否使用单例模式创建连接池实例
            if self.use_pool_singleton:
                self._pool_instance = ConnectionPool.get_instance(pool_config)
                self.logger.info("使用单例模式初始化连接池")
            else:
                self._pool_instance = ConnectionPool(pool_config)
                self.logger.info("使用普通模式初始化连接池")
            
            self._pool = pool_config  # 保持向后兼容性
            
            self.logger.info("通用连接池初始化成功")
            self.logger.info(f"连接池配置: {self._pool_instance.get_pool_status()}")
            
        except ConnectionPoolError as e:
            self.logger.error(f"连接池初始化失败: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"连接池初始化失败: {str(e)}")
            raise
    
    @contextmanager
    def get_connection(self, timeout: Optional[float] = None):
        """
        获取数据库连接的上下文管理器
        
        Args:
            timeout: 获取连接的超时时间（秒），仅在使用连接池时有效
        """
        conn = None
        pooled_conn = None
        try:
            if self.use_pool and self._pool_instance:
                # 使用通用连接池
                pooled_conn = self._pool_instance.get_connection(timeout)
                conn = pooled_conn.get_raw_connection()
            elif self.use_pool and self._pool:
                # 向后兼容：使用传统方式
                conn = pymysql.connect(**self._pool)
            else:
                # 不使用连接池
                conn = pymysql.connect(
                    host=self.config['host'],
                    port=self.config['port'],
                    user=self.config['user'],
                    password=self.config['password'],
                    database=self.config['database'],
                    charset=self.config['charset'],
                    cursorclass=DictCursor,
                    autocommit=self.config['autocommit'],
                    connect_timeout=self.config['connect_timeout']
                )
            
            yield conn
            
        except ConnectionPoolError as e:
            self.logger.error(f"连接池错误: {str(e)}")
            raise
        except OperationalError as e:
            self.logger.error(f"数据库连接失败: {str(e)}")
            raise
        finally:
            if pooled_conn:
                # 使用连接池时，归还连接到池中
                pooled_conn.close()
            elif conn and not self.use_pool:
                # 不使用连接池时，直接关闭连接
                conn.close()
    
    def connect(self, timeout: Optional[float] = None) -> Connection:
        """
        建立数据库连接
        
        Args:
            timeout: 获取连接的超时时间（秒），仅在使用连接池时有效
            
        Returns:
            pymysql.Connection: 数据库连接对象
        """
        try:
            if self.use_pool and self._pool_instance:
                # 使用通用连接池获取连接
                pooled_conn = self._pool_instance.get_connection(timeout)
                self.connection = pooled_conn.get_raw_connection()
                # 存储pooled_conn以便后续归还
                self._current_pooled_conn = pooled_conn
            elif self.use_pool and self._pool:
                # 向后兼容：使用传统方式
                self.connection = pymysql.connect(**self._pool)
            else:
                # 不使用连接池
                self.connection = pymysql.connect(
                    host=self.config['host'],
                    port=self.config['port'],
                    user=self.config['user'],
                    password=self.config['password'],
                    database=self.config['database'],
                    charset=self.config['charset'],
                    cursorclass=DictCursor,
                    autocommit=self.config['autocommit'],
                    connect_timeout=self.config['connect_timeout']
                )
            
            self.logger.info("数据库连接成功")
            return self.connection
            
        except ConnectionPoolError as e:
            self.logger.error(f"连接池错误: {str(e)}")
            raise
        except OperationalError as e:
            self.logger.error(f"数据库连接失败: {str(e)}")
            raise
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self.connection:
            try:
                # 如果使用连接池，归还连接到池中
                if hasattr(self, '_current_pooled_conn') and self._current_pooled_conn:
                    self._current_pooled_conn.close()
                    self._current_pooled_conn = None
                else:
                    # 传统方式，直接关闭连接
                    self.connection.close()
                
                self.connection = None
                self.logger.info("数据库连接已关闭")
            except Exception as e:
                self.logger.error(f"关闭连接时出错: {str(e)}")
    
    def get_pool_status(self) -> Optional[Dict[str, Any]]:
        """
        获取连接池状态信息
        
        Returns:
            Dict: 连接池状态信息，如果未使用连接池则返回None
        """
        if self.use_pool and self._pool_instance:
            return self._pool_instance.get_pool_status()
        return None
    
    def close_pool(self) -> None:
        """
        关闭连接池
        注意：关闭后无法重新打开，需要重新创建MySqlTool实例
        """
        if self._pool_instance:
            try:
                self._pool_instance.close()
                self.logger.info("连接池已关闭")
            except Exception as e:
                self.logger.error(f"关闭连接池时出错: {str(e)}")
                raise
    
    def __enter__(self):
        """上下文管理器入口"""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    def get_tables(self, database: Optional[str] = None) -> List[str]:
        """
        获取数据库中的所有表名
        
        Args:
            database: 数据库名，如果为None则使用默认数据库
            
        Returns:
            List[str]: 表名列表
        """
        db_name = database or self.config['database']
        sql = "SHOW TABLES"
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    # 提取表名（字典的values）
                    tables = [list(row.values())[0] for row in result]
                    return tables
                    
        except Exception as e:
            self.logger.error(f"获取表列表失败: {str(e)}")
            raise
    
    def get_table_structure(self, table_name: str, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取表的详细结构信息
        
        Args:
            table_name: 表名
            database: 数据库名，如果为None则使用默认数据库
            
        Returns:
            List[Dict]: 字段信息列表，每个字段包含：
                - Field: 字段名
                - Type: 数据类型
                - Null: 是否允许为空
                - Key: 键类型（PRI, UNI, MUL）
                - Default: 默认值
                - Extra: 额外信息
                - Comment: 字段注释
        """
        db_name = database or self.config['database']
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 获取基本字段信息
                    sql = f"SHOW FULL COLUMNS FROM `{table_name}` FROM `{db_name}`"
                    cursor.execute(sql)
                    columns = cursor.fetchall()
                    
                    # 获取表注释
                    cursor.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
                    table_info = cursor.fetchone()
                    
                    result = []
                    for column in columns:
                        result.append({
                            'Field': column['Field'],
                            'Type': column['Type'],
                            'Null': column['Null'],
                            'Key': column['Key'],
                            'Default': column['Default'],
                            'Extra': column['Extra'],
                            'Comment': column.get('Comment', '')
                        })
                    
                    return result
                    
        except Exception as e:
            self.logger.error(f"获取表结构失败: {str(e)}")
            raise
    
    def create_table(self, table_name: str, fields: List[Dict[str, Any]], 
                    drop_if_exists: bool = False, database: Optional[str] = None) -> bool:
        """
        创建数据表
        
        Args:
            table_name: 表名
            fields: 字段定义列表，每个字段包含：
                - name: 字段名（必填）
                - type: 数据类型（必填，如VARCHAR(255), INT, DATETIME等）
                - nullable: 是否允许为空（可选，默认True）
                - primary_key: 是否为主键（可选，默认False）
                - unique: 是否唯一（可选，默认False）
                - default: 默认值（可选）
                - comment: 字段注释（可选）
                - auto_increment: 是否自增（可选，默认False）
            drop_if_exists: 如果表已存在是否删除重建
            database: 数据库名，如果为None则使用默认数据库
            
        Returns:
            bool: 创建成功返回True，失败返回False
            
        Example:
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
                }
            ]
        """
        db_name = database or self.config['database']
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 检查表是否存在
                    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                    if cursor.fetchone():
                        if drop_if_exists:
                            cursor.execute(f"DROP TABLE `{table_name}`")
                            self.logger.info(f"表 {table_name} 已存在，已删除重建")
                        else:
                            self.logger.info(f"表 {table_name} 已存在，跳过创建")
                            return True
                    
                    # 构建建表SQL
                    sql_parts = []
                    primary_keys = []
                    
                    for field in fields:
                        field_sql = self._build_field_sql(field)
                        sql_parts.append(field_sql)
                        
                        if field.get('primary_key'):
                            primary_keys.append(f"`{field['name']}`")
                    
                    # 添加主键约束
                    if primary_keys:
                        sql_parts.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
                    
                    create_sql = f"""
                    CREATE TABLE `{table_name}` (
                        {', '.join(sql_parts)}
                    ) ENGINE=InnoDB DEFAULT CHARSET={self.config['charset']}
                    """
                    
                    self.logger.debug(f"建表SQL: {create_sql}")
                    cursor.execute(create_sql)
                    
                    self.logger.info(f"表 {table_name} 创建成功")
                    return True
                    
        except Exception as e:
            self.logger.error(f"创建表失败: {str(e)}")
            return False
    
    def _build_field_sql(self, field: Dict[str, Any]) -> str:
        """构建字段定义SQL"""
        name = field['name']
        field_type = field['type']
        
        parts = [f"`{name}`", field_type]
        
        # 自增
        if field.get('auto_increment'):
            parts.append("AUTO_INCREMENT")
        
        # 非空
        if not field.get('nullable', True):
            parts.append("NOT NULL")
        
        # 默认值
        if 'default' in field:
            default_value = field['default']
            if isinstance(default_value, str):
                parts.append(f"DEFAULT '{default_value}'")
            else:
                parts.append(f"DEFAULT {default_value}")
        
        # 唯一约束
        if field.get('unique'):
            parts.append("UNIQUE")
        
        # 注释
        if field.get('comment'):
            parts.append(f"COMMENT '{field['comment']}'")
        
        return ' '.join(parts)
    
    def execute_sql(self, sql: str, params: Optional[Union[Tuple, Dict, List]] = None, 
                   fetch_all: bool = True, use_transaction: bool = False) -> Union[List[Dict], int, None]:
        """
        执行SQL语句
        
        Args:
            sql: SQL语句
            params: 参数（防止SQL注入）
            fetch_all: 是否获取所有结果（仅对查询语句有效）
            use_transaction: 是否使用事务
            
        Returns:
            查询语句：返回结果列表（字典格式）
            增删改语句：返回影响行数
            其他语句：返回None
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 判断SQL类型
                    sql_type = sql.strip().upper().split()[0]
                    is_query = sql_type in ['SELECT', 'SHOW', 'DESCRIBE', 'DESC']
                    
                    if use_transaction and not self.config['autocommit']:
                        conn.begin()
                    
                    # 执行SQL
                    if params:
                        cursor.execute(sql, params)
                    else:
                        cursor.execute(sql)
                    
                    if is_query:
                        if fetch_all:
                            result = cursor.fetchall()
                        else:
                            result = cursor.fetchone()
                        self.logger.info(f"查询成功，返回{len(result) if isinstance(result, list) else 1}条记录")
                        return result
                    else:
                        affected_rows = cursor.rowcount
                        self.logger.info(f"SQL执行成功，影响{affected_rows}行")
                        return affected_rows
                    
                    if use_transaction and not self.config['autocommit']:
                        conn.commit()
                        
        except Exception as e:
            self.logger.error(f"SQL执行失败: {str(e)}")
            if use_transaction and not self.config['autocommit']:
                conn.rollback()
            raise
    
    def execute_sql_file(self, file_path: str, encoding: str = 'utf-8', 
                        continue_on_error: bool = True) -> Dict[str, Any]:
        """
        批量执行SQL文件
        
        Args:
            file_path: SQL文件路径
            encoding: 文件编码
            continue_on_error: 出错时是否继续执行
            
        Returns:
            Dict: 执行结果统计
                - total: 总语句数
                - success: 成功数
                - failed: 失败数
                - errors: 错误详情列表
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"SQL文件不存在: {file_path}")
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # 解析SQL语句（处理注释和分隔符）
            statements = self._parse_sql_statements(content)
            
            result = {
                'total': len(statements),
                'success': 0,
                'failed': 0,
                'errors': []
            }
            
            self.logger.info(f"开始执行SQL文件，共{result['total']}条语句")
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    for i, statement in enumerate(statements, 1):
                        if not statement.strip():
                            continue
                            
                        try:
                            cursor.execute(statement)
                            result['success'] += 1
                            self.logger.info(f"第{i}条语句执行成功")
                            
                        except Exception as e:
                            result['failed'] += 1
                            error_info = {
                                'statement_index': i,
                                'statement': statement[:200] + '...' if len(statement) > 200 else statement,
                                'error': str(e)
                            }
                            result['errors'].append(error_info)
                            
                            self.logger.error(f"第{i}条语句执行失败: {str(e)}")
                            
                            if not continue_on_error:
                                self.logger.error("停止执行后续语句")
                                break
                    
                    if not self.config['autocommit']:
                        conn.commit()
            
            self.logger.info(f"SQL文件执行完成：成功{result['success']}条，失败{result['failed']}条")
            return result
            
        except Exception as e:
            self.logger.error(f"SQL文件执行失败: {str(e)}")
            raise
    
    def _parse_sql_statements(self, content: str) -> List[str]:
        """解析SQL语句"""
        # 移除注释
        content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # 按分号分割，但考虑引号内的分号
        statements = []
        current_statement = ''
        in_single_quote = False
        in_double_quote = False
        
        for char in content:
            current_statement += char
            
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
            elif char == ';' and not in_single_quote and not in_double_quote:
                statements.append(current_statement.strip())
                current_statement = ''
        
        # 添加最后一条语句（如果没有分号）
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        return [stmt for stmt in statements if stmt.strip()]
    
    def print_table_structure(self, table_name: str, database: Optional[str] = None) -> None:
        """
        格式化打印表结构
        
        Args:
            table_name: 表名
            database: 数据库名
        """
        try:
            structure = self.get_table_structure(table_name, database)
            
            print(f"\n表结构: {table_name}")
            print("-" * 80)
            print(f"{'字段名':<20} {'数据类型':<20} {'可空':<8} {'键':<8} {'默认值':<15} {'注释'}")
            print("-" * 80)
            
            for field in structure:
                print(f"{field['Field']:<20} {field['Type']:<20} {field['Null']:<8} "
                      f"{field['Key']:<8} {str(field['Default']):<15} {field['Comment']}")
            
            print("-" * 80)
            
        except Exception as e:
            self.logger.error(f"打印表结构失败: {str(e)}")
            raise


# 使用示例和测试代码
if __name__ == "__main__":
    print("=== MySqlTool 使用示例 ===\n")
    
    # 示例1: 传统连接方式（不使用连接池）
    print("1. 传统连接方式（不使用连接池）:")
    try:
        db_tool = MySqlTool()
        tables = db_tool.get_tables()
        print(f"   数据库中的表数量: {len(tables)}")
        db_tool.close()
    except Exception as e:
        print(f"   错误: {str(e)}")
    
    # 示例2: 使用连接池（普通模式）
    print("\n2. 使用连接池（普通模式）:")
    try:
        # 连接池配置
        pool_config = {
            'max_connections': 10,
            'min_idle_connections': 3,
            'max_idle_connections': 5,
            'idle_timeout': 300,
            'connect_timeout': 10,
            'retry_times': 3,
            'blocking': True,
            'wait_timeout': 30
        }
        
        db_tool = MySqlTool(pool_config=pool_config, use_pool_singleton=False)
        
        # 获取连接池状态
        pool_status = db_tool.get_pool_status()
        if pool_status:
            print(f"   连接池状态: 总连接数={pool_status['total_connections']}, "
                  f"活跃连接数={pool_status['active_connections']}, "
                  f"空闲连接数={pool_status['idle_connections']}")
        
        # 执行查询
        tables = db_tool.get_tables()
        print(f"   数据库中的表数量: {len(tables)}")
        
        # 演示连接复用（连接池会自动复用连接）
        for i in range(3):
            result = db_tool.execute_sql("SELECT 1")
            print(f"   第{i+1}次查询: {result}")
        
        # 关闭连接池
        db_tool.close_pool()
        
    except Exception as e:
        print(f"   错误: {str(e)}")
    
    # 示例3: 使用连接池（单例模式）
    print("\n3. 使用连接池（单例模式）:")
    try:
        # 连接池配置
        pool_config = {
            'max_connections': 5,
            'min_idle_connections': 2,
            'max_idle_connections': 3,
            'idle_timeout': 300
        }
        
        # 创建第一个实例（使用单例模式）
        db_tool1 = MySqlTool(pool_config=pool_config, use_pool_singleton=True)
        print(f"   实例1 ID: {id(db_tool1._pool_instance)}")
        
        # 创建第二个实例（使用单例模式）
        db_tool2 = MySqlTool(pool_config=pool_config, use_pool_singleton=True)
        print(f"   实例2 ID: {id(db_tool2._pool_instance)}")
        
        # 验证是否为同一实例
        print(f"   是否为同一连接池实例: {db_tool1._pool_instance is db_tool2._pool_instance}")
        
        # 使用第一个实例执行查询
        tables1 = db_tool1.get_tables()
        print(f"   实例1查询 - 数据库中的表数量: {len(tables1)}")
        
        # 使用第二个实例执行查询
        tables2 = db_tool2.get_tables()
        print(f"   实例2查询 - 数据库中的表数量: {len(tables2)}")
        
        # 关闭连接池（只需要关闭一个，因为是单例）
        db_tool1.close_pool()
        
    except Exception as e:
        print(f"   错误: {str(e)}")
    
    # 示例4: 上下文管理器（自动管理连接）
    print("\n4. 上下文管理器（自动管理连接）:")
    try:
        with MySqlTool(pool_config={'max_connections': 5}) as db_tool:
            tables = db_tool.get_tables()
            print(f"   数据库中的表数量: {len(tables)}")
            # 连接会在退出上下文时自动归还到池中
    except Exception as e:
        print(f"   错误: {str(e)}")
    
    # 示例5: 多线程测试连接池（单例模式）
    print("\n5. 多线程测试连接池（单例模式）:")
    import threading
    import time
    
    def worker(thread_id):
        try:
            # 每个线程都创建一个新的MySqlTool实例，但使用同一个连接池单例
            db_tool = MySqlTool(use_pool_singleton=True)
            result = db_tool.execute_sql("SELECT 1")
            pool_status = db_tool.get_pool_status()
            print(f"   线程{thread_id}: 查询成功，连接池状态={pool_status['active_connections']}/{pool_status['total_connections']}, "
                  f"连接池实例ID={id(db_tool._pool_instance)}")
        except Exception as e:
            print(f"   线程{thread_id}: 错误 - {str(e)}")
    
    try:
        # 重置连接池单例（用于演示）
        from connection_pool import ConnectionPool
        ConnectionPool.reset_instance()
        
        threads = []
        
        # 启动10个线程，测试连接池并发处理
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        print(f"   所有线程使用的都是同一个连接池单例实例")
        
    except Exception as e:
        print(f"   错误: {str(e)}")
    
    print("\n=== 示例完成 ===")