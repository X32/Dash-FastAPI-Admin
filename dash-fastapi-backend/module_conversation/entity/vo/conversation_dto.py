from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CreateConversationDTO(BaseModel):
    """
    创建会话请求模型
    """
    title: str = Field(..., min_length=1, max_length=200, description="会话标题")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "关于Python编程的讨论"
            }
        }


class UpdateConversationDTO(BaseModel):
    """
    更新会话请求模型
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="会话标题")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态（1-有效 0-已删除）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "更新后的会话标题",
                "status": 1
            }
        }


class CreateMessageDTO(BaseModel):
    """
    创建消息请求模型
    """
    role: str = Field(..., pattern="^(user|assistant|examiner)$", description="消息角色（user/assistant/examiner）")
    seq: int = Field(..., ge=0, description="消息序号")
    contents: List['CreateMessageContentDTO'] = Field(..., min_items=1, description="消息内容列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "seq": 1,
                "contents": [
                    {
                        "content_type": "text",
                        "text": "请帮我写一个Python函数",
                        "seq": 1
                    }
                ]
            }
        }


class CreateMessageContentDTO(BaseModel):
    """
    创建消息内容请求模型
    """
    content_type: str = Field(..., pattern="^(text|image_url)$", description="内容类型（text/image_url）")
    text: Optional[str] = Field(None, description="文本内容（当content_type=text时使用）")
    image_url: Optional[str] = Field(None, description="图片URL（当content_type=image_url时使用）")
    seq: int = Field(..., ge=0, description="内容序号")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_type": "text",
                "text": "请帮我写一个Python函数",
                "seq": 1
            }
        }


class UpdateMessageDTO(BaseModel):
    """
    更新消息请求模型
    """
    role: Optional[str] = Field(None, pattern="^(user|assistant|examiner)$", description="消息角色")
    seq: Optional[int] = Field(None, ge=0, description="消息序号")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "assistant",
                "seq": 2
            }
        }


class QueryConversationDTO(BaseModel):
    """
    查询会话列表请求模型
    """
    user_id: int = Field(..., gt=0, description="用户ID")
    conversation_id: Optional[int] = Field(None, gt=0, description="会话ID（可选，指定则查询单个会话详情）")
    status: Optional[int] = Field(1, ge=0, le=1, description="状态筛选（1-有效 0-已删除，默认1）")
    page: int = Field(1, ge=1, description="页码（默认1）")
    page_size: int = Field(20, ge=1, le=100, description="每页条数（默认20，最大100）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "status": 1,
                "page": 1,
                "page_size": 20
            }
        }


# 前向引用解决循环依赖
CreateMessageDTO.model_rebuild()