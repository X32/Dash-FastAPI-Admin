from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from config.get_db import get_db
from module_Conversation.service.conversation_service import ConversationService, MessageService


router = APIRouter(prefix='/conversation', tags=['会话管理'])


# Pydantic 模型
class ConversationCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description='会话标题')
    remark: Optional[str] = Field(None, max_length=500, description='备注')


class ConversationUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description='会话标题')
    remark: Optional[str] = Field(None, max_length=500, description='备注')


class MessageContentCreateRequest(BaseModel):
    content_type: str = Field(..., pattern='^(text|image_url)$', description='内容类型（text/image_url）')
    text: Optional[str] = Field(None, description='文本内容')
    image_url: Optional[str] = Field(None, description='图片URL')


class MessageCreateRequest(BaseModel):
    role: str = Field(..., min_length=1, max_length=20, description='角色（user/assistant/examiner等）')
    contents: List[MessageContentCreateRequest] = Field(..., description='消息内容列表')


class MessageUpdateRequest(BaseModel):
    role: Optional[str] = Field(None, min_length=1, max_length=20, description='角色（user/assistant/examiner等）')
    contents: Optional[List[MessageContentCreateRequest]] = Field(None, description='消息内容列表')


# 会话相关接口
@router.post('/create', summary='创建会话')
async def create_conversation(
    request: ConversationCreateRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = 1  # 这里应该从认证信息中获取，暂时硬编码
):
    conversation = await ConversationService.create_conversation(db, user_id, request.title, request.remark)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='创建会话失败')
    return {'code': 0, 'message': '创建成功', 'data': conversation}


@router.get('/detail/{conversation_id}', summary='获取会话详情')
async def get_conversation_detail(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = 1  # 这里应该从认证信息中获取，暂时硬编码
):
    conversation = await ConversationService.get_conversation_detail(db, conversation_id, user_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='会话不存在或无权限访问')
    return {'code': 0, 'message': '获取成功', 'data': conversation}


@router.get('/list', summary='获取会话列表')
async def get_conversation_list(
    page: int = 1,
    page_size: int = 20,
    status: int = 1,
    db: AsyncSession = Depends(get_db),
    user_id: int = 1  # 这里应该从认证信息中获取，暂时硬编码
):
    conversations, total = await ConversationService.get_conversation_list(db, user_id, page, page_size, status)
    return {
        'code': 0,
        'message': '获取成功',
        'data': {
            'list': conversations,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    }


@router.put('/update/{conversation_id}', summary='更新会话信息')
async def update_conversation(
    conversation_id: int,
    request: ConversationUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = 1  # 这里应该从认证信息中获取，暂时硬编码
):
    conversation = await ConversationService.update_conversation(db, conversation_id, user_id, request.title, request.remark)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='会话不存在或无权限访问')
    return {'code': 0, 'message': '更新成功', 'data': conversation}


@router.delete('/delete/{conversation_id}', summary='删除会话')
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = 1  # 这里应该从认证信息中获取，暂时硬编码
):
    success = await ConversationService.delete_conversation(db, conversation_id, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='会话不存在或无权限访问')
    return {'code': 0, 'message': '删除成功'}


# 消息相关接口
@router.post('/{conversation_id}/message/create', summary='创建消息')
async def create_message(
    conversation_id: int,
    request: MessageCreateRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = 1  # 这里应该从认证信息中获取，暂时硬编码
):
    message = await MessageService.create_message(db, conversation_id, user_id, request.role, request.contents)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='会话不存在或无权限访问')
    return {'code': 0, 'message': '创建成功', 'data': message}


@router.get('/message/detail/{message_id}', summary='获取消息详情')
async def get_message_detail(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = 1  # 这里应该从认证信息中获取，暂时硬编码
):
    message = await MessageService.get_message_detail(db, message_id, user_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='消息不存在或无权限访问')
    return {'code': 0, 'message': '获取成功', 'data': message}


@router.put('/message/update/{message_id}', summary='更新消息信息')
async def update_message(
    message_id: int,
    request: MessageUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = 1  # 这里应该从认证信息中获取，暂时硬编码
):
    message = await MessageService.update_message(db, message_id, user_id, request.role, request.contents)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='消息不存在或无权限访问')
    return {'code': 0, 'message': '更新成功', 'data': message}


@router.delete('/message/delete/{message_id}', summary='删除消息')
async def delete_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = 1  # 这里应该从认证信息中获取，暂时硬编码
):
    success = await MessageService.delete_message(db, message_id, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='消息不存在或无权限访问')
    return {'code': 0, 'message': '删除成功'}