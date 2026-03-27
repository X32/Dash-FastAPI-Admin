from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class ConversationVO(BaseModel):
    """
    会话信息响应模型
    """
    conversation_id: int = Field(..., description="会话ID")
    user_id: int = Field(..., description="用户ID")
    title: str = Field(..., description="会话标题")
    status: int = Field(..., description="状态（1-有效 0-已删除）")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class MessageContentVO(BaseModel):
    """
    消息内容响应模型
    """
    content_id: int = Field(..., description="内容ID")
    message_id: int = Field(..., description="消息ID")
    content_type: str = Field(..., description="内容类型（text/image_url）")
    text: Optional[str] = Field(None, description="文本内容")
    image_url: Optional[str] = Field(None, description="图片URL")
    seq: int = Field(..., description="内容序号")
    create_time: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class MessageVO(BaseModel):
    """
    消息信息响应模型
    """
    message_id: int = Field(..., description="消息ID")
    conversation_id: int = Field(..., description="会话ID")
    role: str = Field(..., description="消息角色（user/assistant/examiner等）")
    seq: int = Field(..., description="消息序号")
    create_time: datetime = Field(..., description="创建时间")
    contents: List[MessageContentVO] = Field(default_factory=list, description="消息内容列表")
    
    class Config:
        from_attributes = True


class ConversationDetailVO(BaseModel):
    """
    会话详情响应模型（包含消息和内容）
    """
    conversation: ConversationVO = Field(..., description="会话基本信息")
    messages: List[MessageVO] = Field(default_factory=list, description="消息列表")


class ConversationListVO(BaseModel):
    """
    会话列表响应模型
    """
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条数")
    conversations: List[ConversationVO] = Field(default_factory=list, description="会话列表")