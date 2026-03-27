"""
会话管理模块数据库初始化
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)


async def init_conversation_tables(db_session: AsyncSession):
    """
    初始化会话管理相关表
    
    Args:
        db_session: 数据库会话
    """
    try:
        # 创建会话表
        create_conversation_table = """
        CREATE TABLE IF NOT EXISTS `sys_conversation` (
            `conversation_id` bigint NOT NULL AUTO_INCREMENT COMMENT '会话ID',
            `conversation_title` varchar(200) DEFAULT NULL COMMENT '会话标题',
            `user_id` bigint NOT NULL COMMENT '用户ID',
            `status` char(1) DEFAULT '0' COMMENT '状态（0正常 1停用）',
            `del_flag` char(1) DEFAULT '0' COMMENT '删除标志（0代表存在 2代表删除）',
            `create_by` varchar(64) DEFAULT NULL COMMENT '创建者',
            `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            `update_by` varchar(64) DEFAULT NULL COMMENT '更新者',
            `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            `remark` varchar(500) DEFAULT NULL COMMENT '备注',
            PRIMARY KEY (`conversation_id`),
            KEY `idx_user_id` (`user_id`),
            KEY `idx_status` (`status`),
            KEY `idx_del_flag` (`del_flag`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会话表';
        """
        
        # 创建消息表
        create_message_table = """
        CREATE TABLE IF NOT EXISTS `sys_conversation_message` (
            `message_id` bigint NOT NULL AUTO_INCREMENT COMMENT '消息ID',
            `conversation_id` bigint NOT NULL COMMENT '会话ID',
            `parent_message_id` bigint DEFAULT NULL COMMENT '父消息ID',
            `message_type` varchar(20) NOT NULL COMMENT '消息类型（text、image、file等）',
            `sender_type` char(1) NOT NULL COMMENT '发送者类型（U用户 A助手）',
            `sender_id` bigint DEFAULT NULL COMMENT '发送者ID',
            `status` char(1) DEFAULT '0' COMMENT '状态（0正常 1停用）',
            `del_flag` char(1) DEFAULT '0' COMMENT '删除标志（0代表存在 2代表删除）',
            `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            PRIMARY KEY (`message_id`),
            KEY `idx_conversation_id` (`conversation_id`),
            KEY `idx_parent_message_id` (`parent_message_id`),
            KEY `idx_sender_type` (`sender_type`),
            KEY `idx_status` (`status`),
            KEY `idx_del_flag` (`del_flag`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会话消息表';
        """
        
        # 创建消息内容表
        create_message_content_table = """
        CREATE TABLE IF NOT EXISTS `sys_conversation_message_content` (
            `content_id` bigint NOT NULL AUTO_INCREMENT COMMENT '内容ID',
            `message_id` bigint NOT NULL COMMENT '消息ID',
            `content_type` varchar(20) NOT NULL COMMENT '内容类型（text、image、file等）',
            `content` longtext COMMENT '内容',
            `file_name` varchar(255) DEFAULT NULL COMMENT '文件名',
            `file_size` bigint DEFAULT NULL COMMENT '文件大小',
            `file_url` varchar(500) DEFAULT NULL COMMENT '文件URL',
            `mime_type` varchar(100) DEFAULT NULL COMMENT 'MIME类型',
            `status` char(1) DEFAULT '0' COMMENT '状态（0正常 1停用）',
            `del_flag` char(1) DEFAULT '0' COMMENT '删除标志（0代表存在 2代表删除）',
            `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            PRIMARY KEY (`content_id`),
            KEY `idx_message_id` (`message_id`),
            KEY `idx_content_type` (`content_type`),
            KEY `idx_status` (`status`),
            KEY `idx_del_flag` (`del_flag`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会话消息内容表';
        """
        
        # 执行SQL语句
        await db_session.execute(text(create_conversation_table))
        await db_session.execute(text(create_message_table))
        await db_session.execute(text(create_message_content_table))
        
        # 提交事务
        await db_session.commit()
        
        logger.info("会话管理模块数据库表初始化成功")
        
    except Exception as e:
        await db_session.rollback()
        logger.error(f"会话管理模块数据库表初始化失败: {str(e)}")
        raise


async def check_conversation_tables_exist(db_session: AsyncSession) -> bool:
    """
    检查会话管理相关表是否存在
    
    Args:
        db_session: 数据库会话
        
    Returns:
        bool: 表是否存在
    """
    try:
        query = """
        SELECT COUNT(*) as table_count 
        FROM information_schema.tables 
        WHERE table_schema = DATABASE() 
        AND table_name IN ('sys_conversation', 'sys_conversation_message', 'sys_conversation_message_content')
        """
        
        result = await db_session.execute(text(query))
        count = result.scalar()
        
        return count == 3
        
    except Exception as e:
        logger.error(f"检查会话管理表是否存在时出错: {str(e)}")
        return False