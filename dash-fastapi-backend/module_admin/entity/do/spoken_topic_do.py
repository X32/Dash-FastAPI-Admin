from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from config.database import Base


class SysSpokenTopic(Base):
    """
    口语考试话题表
    """

    __tablename__ = 'sys_spoken_topic'

    topic_id = Column(Integer, primary_key=True, autoincrement=True, comment='话题ID')
    category_id = Column(Integer, nullable=False, comment='分类ID')
    topic_name = Column(String(200), nullable=False, comment='话题名称')
    topic_content = Column(Text, nullable=False, comment='话题内容')
    difficulty_level = Column(String(20), nullable=True, default='中等', comment='难度级别（简单、中等、困难）')
    status = Column(String(1), nullable=True, default='0', comment='话题状态（0正常 1停用）')
    del_flag = Column(String(1), nullable=True, default='0', comment='删除标志（0代表存在 2代表删除）')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now(), comment='更新时间')
    remark = Column(String(500), nullable=True, default='', comment='备注')
