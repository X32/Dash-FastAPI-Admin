from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base


class Conversation(Base):
    """
    会话表实体类
    """
    __tablename__ = 'conversations'

    conversation_id = Column(Integer, primary_key=True, autoincrement=True, comment='会话ID')
    user_id = Column(Integer, nullable=False, comment='用户ID（外键）')
    title = Column(String(200), default='', comment='会话标题')
    status = Column(Integer, default=1, comment='状态（1-有效 0-已删除）')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关联关系
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    """
    消息表实体类
    """
    __tablename__ = 'messages'

    message_id = Column(Integer, primary_key=True, autoincrement=True, comment='消息ID')
    conversation_id = Column(Integer, ForeignKey('conversations.conversation_id'), nullable=False, comment='会话ID（外键）')
    role = Column(String(20), nullable=False, comment='消息角色（user/assistant/examiner等）')
    seq = Column(Integer, default=0, comment='消息序号（用于排序）')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')

    # 关联关系
    conversation = relationship("Conversation", back_populates="messages")
    contents = relationship("MessageContent", back_populates="message")


class MessageContent(Base):
    """
    消息内容表实体类
    """
    __tablename__ = 'message_contents'

    content_id = Column(Integer, primary_key=True, autoincrement=True, comment='内容ID')
    message_id = Column(Integer, ForeignKey('messages.message_id'), nullable=False, comment='消息ID（外键）')
    content_type = Column(String(20), nullable=False, comment='内容类型（text/image_url）')
    text = Column(Text, comment='文本内容（当content_type=text时使用）')
    image_url = Column(String(500), comment='图片URL（当content_type=image_url时使用）')
    seq = Column(Integer, default=0, comment='内容序号（同一消息的多部分内容排序）')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')

    # 关联关系
    message = relationship("Message", back_populates="contents")