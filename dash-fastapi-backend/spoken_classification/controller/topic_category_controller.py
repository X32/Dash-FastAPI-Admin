from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from ..service.topic_category_service import TopicCategoryService
from ..entity.topic_category_do import TopicCategoryDO
from config.get_db import get_db
from utils.response_util import ResponseUtil

router = APIRouter(prefix="/topic-category", tags=["话题分类"])

@router.get("/first-level", summary="获取所有一级分类")
def get_first_level_categories(db: Session = Depends(get_db)):
    """
    获取所有一级分类

    返回结果：
    - code: 响应码，0表示成功，非0表示失败
    - message: 响应消息
    - data: 一级分类列表
    """
    try:
        service = TopicCategoryService(db)
        categories = service.get_first_level_categories()
        return ResponseUtil.success(data=categories)
    except Exception as e:
        return ResponseUtil.failure(msg=str(e))

@router.get("/second-level/{parent_id}", summary="获取指定一级分类下的所有二级分类")
def get_second_level_categories(parent_id: int, db: Session = Depends(get_db)):
    """
    获取指定一级分类下的所有二级分类

    参数：
    - parent_id: 一级分类ID

    返回结果：
    - code: 响应码，0表示成功，非0表示失败
    - message: 响应消息
    - data: 二级分类列表
    """
    try:
        service = TopicCategoryService(db)
        categories = service.get_second_level_categories(parent_id)
        return ResponseUtil.success(data=categories)
    except Exception as e:
        return ResponseUtil.failure(msg=str(e))

@router.get("/{id}", summary="根据ID获取分类")
def get_category_by_id(id: int, db: Session = Depends(get_db)):
    """
    根据ID获取分类

    参数：
    - id: 分类ID

    返回结果：
    - code: 响应码，0表示成功，非0表示失败
    - message: 响应消息
    - data: 分类信息
    """
    try:
        service = TopicCategoryService(db)
        category = service.get_by_id(id)
        if category:
            return ResponseUtil.success(data=category)
        else:
            return ResponseUtil.failure(msg=f"分类ID {id} 不存在")
    except Exception as e:
        return ResponseUtil.failure(msg=str(e))

@router.post("/", summary="创建分类")
def create_category(
    category_name: str = Body(..., embed=True, description="分类名称"),
    category_desc: str = Body("", embed=True, description="分类描述"),
    parent_id: int = Body(0, embed=True, description="父分类ID，0表示一级分类"),
    sort_order: int = Body(0, embed=True, description="排序"),
    db: Session = Depends(get_db)
):
    """
    创建分类

    参数：
    - category_name: 分类名称（必填）
    - category_desc: 分类描述（可选，默认值为空字符串）
    - parent_id: 父分类ID（可选，默认值为0，表示一级分类）
    - sort_order: 排序（可选，默认值为0）

    返回结果：
    - code: 响应码，0表示成功，非0表示失败
    - message: 响应消息
    - data: 创建的分类信息
    """
    try:
        service = TopicCategoryService(db)
        category = service.create_category(category_name, category_desc, parent_id, sort_order)
        return ResponseUtil.success(data=category, message="分类创建成功")
    except Exception as e:
        return ResponseUtil.failure(msg=str(e))

@router.put("/{id}", summary="更新分类")
def update_category(
    id: int,
    category_name: str = Body(None, embed=True, description="分类名称"),
    category_desc: str = Body(None, embed=True, description="分类描述"),
    parent_id: int = Body(None, embed=True, description="父分类ID"),
    sort_order: int = Body(None, embed=True, description="排序"),
    db: Session = Depends(get_db)
):
    """
    更新分类

    参数：
    - id: 分类ID（必填）
    - category_name: 分类名称（可选）
    - category_desc: 分类描述（可选）
    - parent_id: 父分类ID（可选）
    - sort_order: 排序（可选）

    返回结果：
    - code: 响应码，0表示成功，非0表示失败
    - message: 响应消息
    - data: 更新后的分类信息
    """
    try:
        service = TopicCategoryService(db)
        category = service.update_category(id, category_name, category_desc, parent_id, sort_order)
        return ResponseUtil.success(data=category, message="分类更新成功")
    except Exception as e:
        return ResponseUtil.failure(msg=str(e))

@router.delete("/{id}", summary="删除分类")
def delete_category(id: int, db: Session = Depends(get_db)):
    """
    删除分类

    参数：
    - id: 分类ID（必填）

    返回结果：
    - code: 响应码，0表示成功，非0表示失败
    - message: 响应消息
    """
    try:
        service = TopicCategoryService(db)
        success = service.delete_category(id)
        if success:
            return ResponseUtil.success(message="分类删除成功")
        else:
            return ResponseUtil.failure(msg=f"分类ID {id} 不存在")
    except Exception as e:
        return ResponseUtil.failure(msg=str(e))