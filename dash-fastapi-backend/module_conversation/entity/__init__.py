# 实体模块初始化文件
from module_conversation.entity.do.conversation_do import Conversation, Message, MessageContent
from module_conversation.entity.vo.conversation_vo import (
    ConversationVO, MessageContentVO, MessageVO, 
    ConversationDetailVO, ConversationListVO
)
from module_conversation.entity.vo.conversation_dto import (
    CreateConversationDTO, UpdateConversationDTO, CreateMessageDTO,
    CreateMessageContentDTO, UpdateMessageDTO, QueryConversationDTO
)

__all__ = [
    'Conversation', 'Message', 'MessageContent',
    'ConversationVO', 'MessageContentVO', 'MessageVO', 
    'ConversationDetailVO', 'ConversationListVO',
    'CreateConversationDTO', 'UpdateConversationDTO', 'CreateMessageDTO',
    'CreateMessageContentDTO', 'UpdateMessageDTO', 'QueryConversationDTO'
]