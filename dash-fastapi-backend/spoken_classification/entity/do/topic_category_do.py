from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from config.database import Base


class TopicCategory(Base):
    """
    话题分类表
    """

    __tablename__ = 'topic_category'

    category_id = Column(Integer, primary_key=True, autoincrement=True, comment='分类ID')
    parent_id = Column(Integer, default=0, comment='父分类ID')
    category_name = Column(String(50), nullable=False, comment='分类名称')
    description = Column(String(200), nullable=True, default='', comment='分类描述')
    order_num = Column(Integer, default=0, comment='显示顺序')
    del_flag = Column(String(1), nullable=True, default='0', comment='删除标志（0代表存在 2代表删除）')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now(), comment='更新时间')