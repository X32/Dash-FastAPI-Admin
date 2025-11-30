from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from config.database import Base


class Conversation(Base):
    """
    会话表
    """

    __tablename__ = 'conversations'

    conversation_id = Column(Integer, primary_key=True, autoincrement=True, comment='会话ID')
    user_id = Column(BigInteger, ForeignKey('sys_user.user_id', ondelete='CASCADE'), nullable=False, comment='用户ID', index=True)
    title = Column(String(255), nullable=False, comment='会话标题')
    status = Column(Integer, default=1, comment='会话状态（1-有效/0-已删除）')
    create_time = Column(DateTime, comment='创建时间', default=datetime.now())
    update_time = Column(DateTime, comment='更新时间', default=datetime.now())
    remark = Column(String(500), default=None, comment='备注')

    # 关联关系
    messages = relationship('Message', back_populates='conversation', cascade='all, delete-orphan')
    user = relationship('SysUser', back_populates='conversations')


class Message(Base):
    """
    消息表
    """

    __tablename__ = 'messages'

    message_id = Column(Integer, primary_key=True, autoincrement=True, comment='消息ID')
    conversation_id = Column(Integer, ForeignKey('conversations.conversation_id', ondelete='CASCADE'), nullable=False, comment='会话ID')
    role = Column(String(20), nullable=False, comment='角色（user/assistant/examiner等）')
    seq = Column(Integer, nullable=False, comment='消息序列')
    create_time = Column(DateTime, comment='创建时间', default=datetime.now())
    update_time = Column(DateTime, comment='更新时间', default=datetime.now())

    # 关联关系
    conversation = relationship('Conversation', back_populates='messages')
    message_contents = relationship('MessageContent', back_populates='message', cascade='all, delete-orphan')


class MessageContent(Base):
    """
    消息内容表
    """

    __tablename__ = 'message_contents'

    content_id = Column(Integer, primary_key=True, autoincrement=True, comment='内容ID')
    message_id = Column(Integer, ForeignKey('messages.message_id', ondelete='CASCADE'), nullable=False, comment='消息ID')
    content_type = Column(String(20), nullable=False, comment='内容类型（text/image_url）')
    text = Column(Text, default=None, comment='文本内容')
    image_url = Column(String(255), default=None, comment='图片URL')
    seq = Column(Integer, nullable=False, comment='内容序列')
    create_time = Column(DateTime, comment='创建时间', default=datetime.now())

    # 关联关系
    message = relationship('Message', back_populates='message_contents')