from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from config.database import Base


class SysSpeakingTopic(Base):
    """
    口语考试话题表
    """

    __tablename__ = 'sys_speaking_topic'

    topic_id = Column(Integer, primary_key=True, autoincrement=True, comment='话题id')
    category_id = Column(Integer, nullable=False, comment='分类id')
    topic_title = Column(String(100), nullable=False, comment='话题标题')
    topic_content = Column(Text, nullable=True, comment='话题内容')
    difficulty_level = Column(String(1), nullable=True, default='1', comment='难度等级（1简单 2中等 3困难）')
    status = Column(String(1), nullable=True, default='0', comment='话题状态（0正常 1停用）')
    del_flag = Column(String(1), nullable=True, default='0', comment='删除标志（0代表存在 2代表删除）')
    create_by = Column(String(64), nullable=True, default='', comment='创建者')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')
    update_by = Column(String(64), nullable=True, default='', comment='更新者')
    update_time = Column(DateTime, nullable=True, default=datetime.now(), comment='更新时间')
    remark = Column(String(500), nullable=True, default='', comment='备注')