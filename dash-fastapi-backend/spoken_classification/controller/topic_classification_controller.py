from typing import List, Tuple
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from config.get_db import get_db
from exceptions.exception import BusinessException
from utils.response_util import ResponseUtil
from spoken_classification.entity.topic_classification import (
    TopicClassificationEntity,
    TopicClassificationCreateRequest,
    TopicClassificationUpdateRequest,
    TopicClassificationQueryRequest
)
from spoken_classification.service.topic_classification_service import TopicClassificationService


router = APIRouter(prefix="/api/topic-classification", tags=["话题分类管理"])


@router.post("/create", summary="创建话题分类")
async def create_classification(
    request: TopicClassificationCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    创建话题分类
    - **name**: 分类名称（必填，最大长度50）
    - **description**: 分类描述（可选，最大长度200）
    - **parent_id**: 父分类ID（可选，默认0表示一级分类）
    - **sort_order**: 排序序号（可选，默认0，越小越靠前）
    """
    try:
        service = TopicClassificationService(db)
        classification = await service.create_classification(request)
        return ResponseUtil.success(data=classification.__dict__)
    except BusinessException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.args[0])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/update", summary="更新话题分类")
async def update_classification(
    request: TopicClassificationUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    更新话题分类
    - **id**: 分类ID（必填）
    - **name**: 分类名称（必填，最大长度50）
    - **description**: 分类描述（可选，最大长度200）
    - **parent_id**: 父分类ID（可选，默认0表示一级分类）
    - **sort_order**: 排序序号（可选，默认0，越小越靠前）
    """
    try:
        service = TopicClassificationService(db)
        classification = await service.update_classification(request)
        return ResponseUtil.success(data=classification.__dict__)
    except BusinessException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.args[0])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/delete/{id}", summary="删除话题分类")
async def delete_classification(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除话题分类
    - **id**: 分类ID（必填）
    """
    try:
        service = TopicClassificationService(db)
        success = await service.delete_classification(id)
        if success:
            return ResponseUtil.success(message="删除成功")
        else:
            return ResponseUtil.error(message="删除失败")
    except BusinessException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.args[0])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/batch-delete", summary="批量删除话题分类")
async def batch_delete_classification(
    ids: List[int],
    db: AsyncSession = Depends(get_db)
):
    """
    批量删除话题分类
    - **ids**: 分类ID列表（必填）
    """
    try:
        service = TopicClassificationService(db)
        success_count, failed_ids = await service.batch_delete_classification(ids)
        data = {
            "success_count": success_count,
            "failed_count": len(failed_ids),
            "failed_ids": failed_ids
        }
        if failed_ids:
            return ResponseUtil.failure(data=data, msg=f"成功删除{success_count}个分类，{len(failed_ids)}个分类删除失败")
        else:
            return ResponseUtil.success(data=data, msg=f"成功删除{success_count}个分类")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/get/{id}", summary="根据ID获取话题分类")
async def get_classification_by_id(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    根据ID获取话题分类
    - **id**: 分类ID（必填）
    """
    try:
        service = TopicClassificationService(db)
        classification = await service.get_classification_by_id(id)
        if classification:
            return ResponseUtil.success(data=classification.__dict__)
        else:
            return ResponseUtil.error(message="分类不存在")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/first-level", summary="获取一级话题分类列表")
async def get_first_level_classifications(
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    获取一级话题分类列表（分页）
    - **page**: 页码（可选，默认1）
    - **page_size**: 每页大小（可选，默认10，最大100）
    """
    try:
        service = TopicClassificationService(db)
        classifications, total = await service.get_first_level_classifications(page, page_size)
        data = {
            "list": [item.__dict__ for item in classifications],
            "total": total,
            "page": page,
            "page_size": page_size
        }
        return ResponseUtil.success(data=data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/second-level/{parent_id}", summary="获取指定一级分类下的二级话题分类列表")
async def get_second_level_classifications(
    parent_id: int,
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定一级分类下的二级话题分类列表（分页）
    - **parent_id**: 一级分类ID（必填）
    - **page**: 页码（可选，默认1）
    - **page_size**: 每页大小（可选，默认10，最大100）
    """
    try:
        service = TopicClassificationService(db)
        classifications, total = await service.get_second_level_classifications(parent_id, page, page_size)
        data = {
            "list": [item.__dict__ for item in classifications],
            "total": total,
            "page": page,
            "page_size": page_size
        }
        return ResponseUtil.success(data=data)
    except BusinessException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.args[0])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/list", summary="根据父ID获取话题分类列表")
async def get_classifications_by_parent_id(
    request: TopicClassificationQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    根据父ID获取话题分类列表（分页）
    - **parent_id**: 父分类ID（可选，默认0表示一级分类）
    - **page**: 页码（可选，默认1）
    - **page_size**: 每页大小（可选，默认10，最大100）
    """
    try:
        service = TopicClassificationService(db)
        classifications, total = await service.get_classifications_by_parent_id(
            request.parent_id or 0, request.page, request.page_size
        )
        data = {
            "list": [item.__dict__ for item in classifications],
            "total": total,
            "page": request.page,
            "page_size": request.page_size
        }
        return ResponseUtil.success(data=data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))