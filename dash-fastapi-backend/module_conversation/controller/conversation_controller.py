from typing import Optional
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from module_conversation.service.conversation_service import ConversationService, MessageService
from module_conversation.entity.vo.conversation_dto import (
    CreateConversationDTO, UpdateConversationDTO, CreateMessageDTO, UpdateMessageDTO, QueryConversationDTO
)
from module_conversation.entity.vo.conversation_vo import (
    ConversationVO, ConversationDetailVO, ConversationListVO, MessageVO
)
from module_conversation.exception.conversation_exception import ConversationException
from config.get_db import get_db


router = APIRouter(prefix="/conversations", tags=["会话管理"])
conversation_service = ConversationService()
message_service = MessageService()


@router.post("/", response_model=ConversationVO, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    dto: CreateConversationDTO,
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新会话
    """
    return await conversation_service.create_conversation(db, user_id, dto)


@router.get("/list", response_model=ConversationListVO)
async def get_conversation_list(
    user_id: int = Query(..., description="用户ID"),
    status: Optional[int] = Query(None, description="会话状态：1-有效，0-已删除"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户会话列表（分页）
    """
    query_dto = QueryConversationDTO(
        user_id=user_id,
        status=status,
        page=page,
        page_size=page_size
    )
    return await conversation_service.get_conversation_list(db, query_dto)


@router.get("/{conversation_id}", response_model=ConversationDetailVO)
async def get_conversation_detail(
    conversation_id: int = Path(..., description="会话ID"),
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取会话详情（包含消息和内容）
    """
    return await conversation_service.get_conversation_detail(db, user_id, conversation_id)


@router.put("/{conversation_id}", response_model=ConversationVO)
async def update_conversation(
    dto: UpdateConversationDTO,
    conversation_id: int = Path(..., description="会话ID"),
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    更新会话信息
    """
    return await conversation_service.update_conversation(db, user_id, conversation_id, dto)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int = Path(..., description="会话ID"),
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    删除会话（软删除）
    """
    await conversation_service.delete_conversation(db, user_id, conversation_id)


# 消息相关接口
@router.post("/{conversation_id}/messages", response_model=MessageVO, status_code=status.HTTP_201_CREATED)
async def create_message(
    dto: CreateMessageDTO,
    conversation_id: int = Path(..., description="会话ID"),
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    创建消息及其内容
    """
    return await message_service.create_message_with_contents(db, user_id, conversation_id, dto)


@router.put("/messages/{message_id}", response_model=MessageVO)
async def update_message(
    dto: UpdateMessageDTO,
    message_id: int = Path(..., description="消息ID"),
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    更新消息信息
    """
    return await message_service.update_message(db, user_id, message_id, dto)


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int = Path(..., description="消息ID"),
    user_id: int = Query(..., description="用户ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    删除消息（级联删除内容）
    """
    await message_service.delete_message(db, user_id, message_id)