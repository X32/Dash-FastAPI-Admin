"""
会话管理模块配置文件
"""
from typing import Optional
from pydantic import BaseSettings, Field


class ConversationConfig(BaseSettings):
    """会话管理模块配置"""
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = Field(default=20, description="默认分页大小")
    MAX_PAGE_SIZE: int = Field(default=100, description="最大分页大小")
    
    # 消息配置
    MAX_MESSAGE_LENGTH: int = Field(default=4000, description="消息内容最大长度")
    MAX_CONVERSATION_TITLE_LENGTH: int = Field(default=200, description="会话标题最大长度")
    
    # 缓存配置
    CONVERSATION_CACHE_TTL: int = Field(default=3600, description="会话缓存过期时间（秒）")
    MESSAGE_CACHE_TTL: int = Field(default=1800, description="消息缓存过期时间（秒）")
    
    # 权限配置
    ALLOW_DELETE_OWN_CONVERSATION_ONLY: bool = Field(default=True, description="只允许删除自己的会话")
    ALLOW_UPDATE_OWN_CONVERSATION_ONLY: bool = Field(default=True, description="只允许更新自己的会话")
    
    class Config:
        env_prefix = "CONVERSATION_"
        case_sensitive = True


# 全局配置实例
conversation_config = ConversationConfig()


def get_conversation_config() -> ConversationConfig:
    """获取会话管理配置"""
    return conversation_config