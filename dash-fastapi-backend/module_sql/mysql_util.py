import os
import re
import configparser
from typing import Dict, List, Optional, Tuple, Any
import logging
from logging.handlers import RotatingFileHandler

# Third-party dependencies (need to install)
# pip install pymysql python-dotenv
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv


class MySQLTool:
    """
    MySQL database operation tool class
    
    Features:
    - Configurable connection parameters
    - Connection pool support
    - Context manager for connection handling
    - Table structure query
    - Table creation
    - General SQL execution
    - SQL file batch execution
    - Comprehensive exception handling
    - Logging support
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        log_file: Optional[str] = None,
        log_level: int = logging.INFO
    ):
        """
        Initialize MySQLTool
        
        Args:
            config_path: Path to configuration file (.env or config.ini). Defaults to None (auto-detect from project root)
            log_file: Path to log file. Defaults to None (log to console only)
            log_level: Logging level. Defaults to logging.INFO
        """
        # Initialize logger
        self.logger = self._init_logger(log_file, log_level)
        
        # Read configuration
        self.config = self._read_config(config_path)
        
        # Connection pool
        self.pool = None
        
        # Current connection
        self.conn = None
        
        # Current cursor
        self.cursor = None
        
        # Initialize connection pool
        self._init_connection_pool()
    
    def _init_logger(self, log_file: Optional[str], log_level: int) -> logging.Logger:
        """
        Initialize logger
        
        Args:
            log_file: Path to log file
            log_level: Logging level
        
        Returns:
            logging.Logger: Configured logger
        """
        logger = logging.getLogger("MySQLTool")
        logger.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def _read_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Read configuration from file
        
        Args:
            config_path: Path to configuration file
        
        Returns:
            Dict[str, Any]: Configuration parameters
        
        Raises:
            FileNotFoundError: If configuration file not found
            ValueError: If required parameters are missing
        """
        config = {}
        
        # Auto-detect config file if not specified
        if not config_path:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            env_path = os.path.join(project_root, '.env')
            ini_path = os.path.join(project_root, 'config.ini')
            
            if os.path.exists(env_path):
                config_path = env_path
            elif os.path.exists(ini_path):
                config_path = ini_path
            else:
                raise FileNotFoundError("Configuration file not found. Please specify a valid path.")
        
        # Read config based on file type
        if '.env' in config_path:
            load_dotenv(config_path)
            
            # Required parameters
            required_params = ['DB_HOST', 'DB_PORT', 'DB_USERNAME', 'DB_PASSWORD', 'DB_DATABASE']
            for param in required_params:
                value = os.getenv(param)
                if not value:
                    raise ValueError(f"Missing required configuration parameter: {param}")
                config[param.lower()] = value
            
            # Optional parameters
            config['db_charset'] = os.getenv('DB_CHARSET', 'utf8mb4')
            config['db_timeout'] = int(os.getenv('DB_TIMEOUT', 10))
        
        elif config_path.endswith('.ini'):
            config_parser = configparser.ConfigParser()
            config_parser.read(config_path)
            
            if 'mysql' not in config_parser:
                raise ValueError("Missing 'mysql' section in config.ini")
            
            mysql_config = config_parser['mysql']
            
            # Required parameters
            required_params = ['host', 'port', 'user', 'password', 'database']
            for param in required_params:
                if param not in mysql_config:
                    raise ValueError(f"Missing required configuration parameter: {param}")
                config[param] = mysql_config[param]
            
            # Convert port to integer
            config['port'] = int(config['port'])
            
            # Optional parameters
            config['charset'] = mysql_config.get('charset', 'utf8mb4')
            config['timeout'] = int(mysql_config.get('timeout', 10))
        
        else:
            raise ValueError("Unsupported configuration file format. Only .env and .ini are supported.")
        
        return config
    
    def _init_connection_pool(self) -> None:
        """
        Initialize connection pool
        """
        try:
            self.pool = pymysql.connect(
                host=self.config.get('db_host', self.config.get('host')),
                port=int(self.config.get('db_port', self.config.get('port'))),
                user=self.config.get('db_username', self.config.get('user')),
            password=self.config.get('db_password', self.config.get('password')),
            database=self.config.get('db_database', self.config.get('database')),
                charset=self.config.get('db_charset', self.config.get('charset')),
                connect_timeout=self.config.get('db_timeout', self.config.get('timeout')),
                cursorclass=DictCursor,
                autocommit=False
            )
            self.logger.info("Connection pool initialized successfully")
        except pymysql.Error as e:
            self.logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    def connect(self) -> None:
        """
        Establish database connection
        
        Raises:
            pymysql.Error: If connection fails
        """
        try:
            if self.pool and self.pool.open:
                self.conn = self.pool
                self.cursor = self.conn.cursor()
                self.logger.info("Database connection established")
            else:
                self._init_connection_pool()
                self.connect()
        except pymysql.Error as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise
    
    def close(self) -> None:
        """
        Close database connection
        """
        try:
            if self.cursor:
                self.cursor.close()
                self.cursor = None
                self.logger.info("Cursor closed")
            
            if self.conn and self.conn.open:
                self.conn.close()
                self.conn = None
                self.logger.info("Database connection closed")
        except pymysql.Error as e:
            self.logger.error(f"Failed to close database connection: {e}")
    
    def __enter__(self) -> 'MySQLTool':
        """
        Context manager enter method
        
        Returns:
            MySQLTool: Instance of MySQLTool
        """
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context manager exit method
        
        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        if exc_type:
            self.logger.error(f"Exception occurred: {exc_val}")
            if self.conn and not self.conn.get_autocommit():
                self.conn.rollback()
                self.logger.info("Transaction rolled back")
        
        self.close()
    
    def get_all_tables(self, database: Optional[str] = None) -> List[str]:
        """
        Get all table names in the database
        
        Args:
            database: Database name (defaults to configured database)
        
        Returns:
            List[str]: List of table names
        
        Raises:
            pymysql.Error: If query fails
        """
        try:
            if not self.conn or not self.conn.open:
                self.connect()
            
            if database:
                self.conn.select_db(database)
            
            self.cursor.execute("SHOW TABLES")
            tables = [table[next(iter(table))] for table in self.cursor.fetchall()]
            
            self.logger.info(f"Retrieved {len(tables)} tables from database")
            return tables
        except pymysql.Error as e:
            self.logger.error(f"Failed to get all tables: {e}")
            raise
    
    def get_table_structure(self, table_name: str, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get detailed structure of a table
        
        Args:
            table_name: Name of the table
            database: Database name (defaults to configured database)
        
        Returns:
            List[Dict[str, Any]]: List of field information
            
        Raises:
            pymysql.Error: If query fails
        """
        try:
            if not self.conn or not self.conn.open:
                self.connect()
            
            if database:
                self.conn.select_db(database)
            
            self.cursor.execute(f"DESCRIBE {table_name}")
            fields = self.cursor.fetchall()
            
            # Format the result
            formatted_fields = []
            for field in fields:
                formatted_fields.append({
                    'field_name': field['Field'],
                    'data_type': field['Type'],
                    'is_nullable': field['Null'] == 'YES',
                    'key': field['Key'],
                    'default_value': field['Default'],
                    'extra': field['Extra']
                })
            
            self.logger.info(f"Retrieved structure for table: {table_name}")
            return formatted_fields
        except pymysql.Error as e:
            self.logger.error(f"Failed to get table structure: {e}")
            raise
    
    def create_table(
        self,
        table_name: str,
        fields: List[Dict[str, Any]],
        database: Optional[str] = None,
        if_exists: str = 'skip'  # 'skip' or 'replace'
    ) -> bool:
        """
        Create a new table
        
        Args:
            table_name: Name of the table to create
            fields: List of field definitions
                Example: [
                    {'name': 'id', 'type': 'INT', 'primary_key': True, 'auto_increment': True},
                    {'name': 'name', 'type': 'VARCHAR(255)', 'nullable': False, 'comment': 'User name'},
                    {'name': 'email', 'type': 'VARCHAR(255)', 'unique': True, 'comment': 'User email'}
                ]
            database: Database name (defaults to configured database)
            if_exists: Action if table exists. 'skip' or 'replace'. Defaults to 'skip'
        
        Returns:
            bool: True if table created successfully, False otherwise
        
        Raises:
            ValueError: If fields parameter is invalid
            pymysql.Error: If create table fails
        """
        try:
            if not self.conn or not self.conn.open:
                self.connect()
            
            if database:
                self.conn.select_db(database)
            
            # Check if table exists
            self.cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            table_exists = self.cursor.fetchone() is not None
            
            if table_exists:
                if if_exists == 'skip':
                    self.logger.info(f"Table {table_name} already exists, skipping creation")
                    return False
                elif if_exists == 'replace':
                    self.cursor.execute(f"DROP TABLE {table_name}")
                    self.logger.info(f"Table {table_name} dropped, recreating...")
            
            # Build fields SQL
            fields_sql = []
            for field in fields:
                if 'name' not in field or 'type' not in field:
                    raise ValueError("Each field must have 'name' and 'type'")
                
                field_sql = f"{field['name']} {field['type']}"
                
                # Handle primary key
                if field.get('primary_key'):
                    field_sql += " PRIMARY KEY"
                
                # Handle auto increment
                if field.get('auto_increment'):
                    field_sql += " AUTO_INCREMENT"
                
                # Handle nullable
                if not field.get('nullable', True):
                    field_sql += " NOT NULL"
                
                # Handle unique
                if field.get('unique'):
                    field_sql += " UNIQUE"
                
                # Handle default value
                if 'default' in field:
                    default_value = field['default']
                    if isinstance(default_value, str):
                        # Check if it's a MySQL function (contains parentheses or is a known function)
                        if '(' in default_value or default_value.upper() in ['CURRENT_TIMESTAMP', 'CURRENT_DATE', 'CURRENT_TIME']:
                            # Don't wrap function in quotes
                            pass
                        else:
                            default_value = f"'{default_value}'"
                    field_sql += f" DEFAULT {default_value}"
                
                # Handle comment
                if 'comment' in field:
                    field_sql += f" COMMENT '{field['comment']}'"
                
                fields_sql.append(field_sql)
            
            # Handle foreign keys
            foreign_keys = []
            for field in fields:
                if 'foreign_key' in field:
                    fk_info = field['foreign_key']
                    if 'table' not in fk_info or 'field' not in fk_info:
                        raise ValueError("Foreign key must have 'table' and 'field'")
                    
                    foreign_key_sql = f"FOREIGN KEY ({field['name']}) REFERENCES {fk_info['table']}({fk_info['field']})"
                    
                    # Handle on delete
                    if 'on_delete' in fk_info:
                        foreign_key_sql += f" ON DELETE {fk_info['on_delete']}"
                    
                    # Handle on update
                    if 'on_update' in fk_info:
                        foreign_key_sql += f" ON UPDATE {fk_info['on_update']}"
                    
                    foreign_keys.append(foreign_key_sql)
            
            # Build create table SQL
            create_sql = f"CREATE TABLE {table_name} ({', '.join(fields_sql + foreign_keys)}) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            
            self.cursor.execute(create_sql)
            self.conn.commit()
            
            self.logger.info(f"Table {table_name} created successfully")
            return True
        except pymysql.Error as e:
            self.logger.error(f"Failed to create table: {e}")
            self.conn.rollback()
            return False
        except ValueError as e:
            self.logger.error(f"Invalid fields parameter: {e}")
            return False
    
    def execute_sql(
        self,
        sql: str,
        params: Optional[Tuple[Any, ...]] = None,
        commit: bool = False
    ) -> Any:
        """
        Execute SQL statement
        
        Args:
            sql: SQL statement to execute
            params: Parameters for parameterized query
            commit: Whether to commit transaction after execution
        
        Returns:
            Any: Query results for SELECT statements, affected rows for INSERT/UPDATE/DELETE statements
        
        Raises:
            pymysql.Error: If SQL execution fails
        """
        try:
            if not self.conn or not self.conn.open:
                self.connect()
            
            self.cursor.execute(sql, params)
            
            if commit:
                self.conn.commit()
                self.logger.info("Transaction committed")
            
            # Check if it's a SELECT statement
            if sql.strip().upper().startswith('SELECT'):
                result = self.cursor.fetchall()
                self.logger.info(f"SELECT executed successfully, returned {len(result)} rows")
                return result
            else:
                affected_rows = self.cursor.rowcount
                self.logger.info(f"SQL executed successfully, affected {affected_rows} rows")
                return affected_rows
        except pymysql.Error as e:
            self.logger.error(f"Failed to execute SQL: {e}")
            self.logger.error(f"SQL: {sql}")
            if params:
                self.logger.error(f"Parameters: {params}")
            
            if not self.conn.get_autocommit():
                self.conn.rollback()
                self.logger.info("Transaction rolled back")
            
            raise
    
    def execute_sql_file(
        self,
        file_path: str,
        encoding: str = 'utf-8',
        continue_on_error: bool = False,
        database: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute SQL statements from a file
        
        Args:
            file_path: Path to SQL file
            encoding: File encoding. Defaults to 'utf-8'
            continue_on_error: Whether to continue executing other statements if one fails. Defaults to False
            database: Database name (defaults to configured database)
        
        Returns:
            Dict[str, Any]: Execution summary
        
        Raises:
            FileNotFoundError: If SQL file not found
            IOError: If failed to read SQL file
        """
        try:
            # Read SQL file
            with open(file_path, 'r', encoding=encoding) as f:
                sql_content = f.read()
        
        except FileNotFoundError:
            self.logger.error(f"SQL file not found: {file_path}")
            raise
        except IOError as e:
            self.logger.error(f"Failed to read SQL file: {e}")
            raise
        
        # Split SQL statements
        sql_statements = self._split_sql_statements(sql_content)
        
        # Execute statements
        total = len(sql_statements)
        success = 0
        failed = 0
        failed_details = []
        
        try:
            if not self.conn or not self.conn.open:
                self.connect()
            
            if database:
                self.conn.select_db(database)
            
            for i, sql in enumerate(sql_statements, 1):
                try:
                    self.cursor.execute(sql)
                    self.conn.commit()
                    success += 1
                    self.logger.info(f"Executed statement {i}/{total} successfully")
                except pymysql.Error as e:
                    failed += 1
                    error_msg = f"Statement {i}/{total} failed: {e}"
                    self.logger.error(error_msg)
                    self.logger.error(f"SQL: {sql}")
                    
                    failed_details.append({
                        'statement_number': i,
                        'sql': sql,
                        'error': str(e)
                    })
                    
                    if not continue_on_error:
                        self.logger.error("Stopping execution due to error")
                        break
                    
                    # Rollback current statement if in transaction
                    if not self.conn.get_autocommit():
                        self.conn.rollback()
        
        except pymysql.Error as e:
            self.logger.error(f"Failed to execute SQL file: {e}")
        
        # Prepare summary
        summary = {
            'total_statements': total,
            'success_count': success,
            'failed_count': failed,
            'failed_details': failed_details
        }
        
        self.logger.info(f"SQL file execution completed: Total={total}, Success={success}, Failed={failed}")
        return summary
    
    def _split_sql_statements(self, sql_content: str) -> List[str]:
        """
        Split SQL content into individual statements
        
        Args:
            sql_content: SQL content
        
        Returns:
            List[str]: List of SQL statements
        """
        # Remove comments
        sql_content = re.sub(r'--.*?$', '', sql_content, flags=re.MULTILINE)  # Line comments
        sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)  # Block comments
        
        # Split by semicolon
        sql_statements = re.split(r';\s*(?=(?:[^\']*\'[^\']*\')*[^\']*$)', sql_content)
        
        # Remove empty statements
        sql_statements = [stmt.strip() for stmt in sql_statements if stmt.strip()]
        
        return sql_statements


if __name__ == '__main__':
    """
    Usage example
    """
    try:
        # Create MySQLTool instance
        mysql_tool = MySQLTool(
            config_path='../.env.dev',
            log_file='mysql_tool.log'
        )
        
        # Example 1: Get all tables
        print("=== Example 1: Get all tables ===")
        tables = mysql_tool.get_all_tables()
        print(f"Tables: {tables}")
        
        # Example 2: Get table structure
        print("\n=== Example 2: Get table structure ===")
        if tables:
            table_structure = mysql_tool.get_table_structure(tables[0])
            print(f"Table structure: {table_structure}")
        
        # Example 3: Create table
        print("\n=== Example 3: Create table ===")
        fields = [
            {'name': 'id', 'type': 'INT', 'primary_key': True, 'auto_increment': True},
            {'name': 'name', 'type': 'VARCHAR(255)', 'nullable': False, 'comment': 'User name'},
            {'name': 'email', 'type': 'VARCHAR(255)', 'unique': True, 'comment': 'User email'},
            {'name': 'age', 'type': 'INT', 'nullable': True, 'comment': 'User age'},
            {'name': 'create_time', 'type': 'DATETIME', 'nullable': False, 'default': 'CURRENT_TIMESTAMP', 'comment': 'Create time'}
        ]
        
        created = mysql_tool.create_table('test_users', fields, if_exists='replace')
        print(f"Table created: {created}")
        
        # Example 4: Execute SQL
        print("\n=== Example 4: Execute SQL ===")
        sql = "INSERT INTO test_users (name, email, age) VALUES (%s, %s, %s)"
        params = ('John Doe', 'john@example.com', 30)
        affected_rows = mysql_tool.execute_sql(sql, params, commit=True)
        print(f"Affected rows: {affected_rows}")
        
        # Example 5: Query data
        print("\n=== Example 5: Query data ===")
        sql = "SELECT * FROM test_users WHERE name = %s"
        params = ('John Doe',)
        results = mysql_tool.execute_sql(sql, params)
        print(f"Query results: {results}")
        
        # Close connection
        mysql_tool.close()
        
    except Exception as e:
        print(f"Error: {e}")