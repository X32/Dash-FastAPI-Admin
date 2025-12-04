from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, String
from config.database import Base


class TopicClassificationEntity(Base):
    """话题分类实体类"""
    __tablename__ = 'topic_classification'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    name = Column(String(50), nullable=False, comment='分类名称')
    description = Column(String(200), nullable=True, default='', comment='分类描述')
    parent_id = Column(Integer, nullable=False, default=0, comment='父分类ID，0表示一级分类')
    sort_order = Column(Integer, nullable=False, default=0, comment='排序序号，越小越靠前')
    is_deleted = Column(Integer, nullable=False, default=0, comment='是否删除，0-未删除，1-已删除')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')
    update_time = Column(DateTime, nullable=True, default=datetime.now(), comment='更新时间')


class TopicClassificationCreateRequest(BaseModel):
    """创建话题分类请求模型"""
    name: str = Field(..., max_length=50, description="分类名称")
    description: Optional[str] = Field("", max_length=200, description="分类描述")
    parent_id: int = Field(0, ge=0, description="父分类ID，0表示一级分类")
    sort_order: int = Field(0, ge=0, description="排序序号，越小越靠前")

    class Config:
        schema_extra = {
            "example": {
                "name": "人工智能",
                "description": "人工智能技术话题",
                "parent_id": 1,
                "sort_order": 1
            }
        }


class TopicClassificationUpdateRequest(BaseModel):
    """更新话题分类请求模型"""
    id: int = Field(..., description="分类ID")
    name: str = Field(..., max_length=50, description="分类名称")
    description: Optional[str] = Field("", max_length=200, description="分类描述")
    parent_id: int = Field(0, ge=0, description="父分类ID，0表示一级分类")
    sort_order: int = Field(0, ge=0, description="排序序号，越小越靠前")

    class Config:
        schema_extra = {
            "example": {
                "id": 4,
                "name": "人工智能技术",
                "description": "人工智能相关技术话题",
                "parent_id": 1,
                "sort_order": 1
            }
        }


class TopicClassificationQueryRequest(BaseModel):
    """查询话题分类请求模型"""
    parent_id: Optional[int] = Field(None, ge=0, description="父分类ID，0表示一级分类")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页大小")

    class Config:
        schema_extra = {
            "example": {
                "parent_id": 1,
                "page": 1,
                "page_size": 10
            }
        }