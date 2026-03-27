from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TopicCategoryDO(Base):
    __tablename__ = 'topic_category'
    __table_args__ = (
        UniqueConstraint('category_name', 'parent_id', 'is_deleted', name='uk_name_parent'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='分类ID')
    category_name = Column(String(50), nullable=False, comment='分类名称')
    category_desc = Column(String(200), default='', comment='分类描述')
    parent_id = Column(BigInteger, default=0, comment='父分类ID，0表示一级分类')
    sort_order = Column(Integer, default=0, comment='排序')
    is_deleted = Column(Boolean, default=False, comment='是否删除，0未删除，1已删除')
    created_time = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def __repr__(self):
        return f"<TopicCategoryDO(id={self.id}, category_name={self.category_name}, parent_id={self.parent_id})>"