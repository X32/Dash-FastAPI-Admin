from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.service.login_service import LoginService
from module_admin.entity.vo.user_vo import CurrentUserModel
from spoken_classification.entity.vo.topic_category_vo import (
    DeleteTopicCategoryModel,
    TopicCategoryModel,
)
from spoken_classification.service.topic_category_service import TopicCategoryService
from utils.log_util import logger
from utils.response_util import ResponseUtil


topicCategoryController = APIRouter(
    prefix='/spoken_classification/topic_category',
    dependencies=[Depends(LoginService.get_current_user)]
)


@topicCategoryController.get(
    '/first_level',
    response_model=List[TopicCategoryModel],
    dependencies=[Depends(CheckUserInterfaceAuth('spoken_classification:topic_category:list'))],
    summary='获取一级分类列表'
)
async def get_first_level_topic_categories(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
):
    """
    获取一级话题分类列表
    """
    category_list_result = await TopicCategoryService.get_first_level_categories_services(query_db)
    logger.info('获取一级话题分类列表成功')

    return ResponseUtil.success(data=category_list_result)


@topicCategoryController.get(
    '/second_level/{parent_id}',
    response_model=List[TopicCategoryModel],
    dependencies=[Depends(CheckUserInterfaceAuth('spoken_classification:topic_category:list'))],
    summary='获取指定一级分类下的二级分类列表'
)
async def get_second_level_topic_categories(
    request: Request,
    parent_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """
    获取指定一级分类下的二级话题分类列表
    """
    category_list_result = await TopicCategoryService.get_second_level_categories_services(query_db, parent_id)
    logger.info(f'获取一级分类ID {parent_id} 下的二级话题分类列表成功')

    return ResponseUtil.success(data=category_list_result)


@topicCategoryController.get(
    '/tree',
    response_model=List[TopicCategoryModel],
    dependencies=[Depends(CheckUserInterfaceAuth('spoken_classification:topic_category:list'))],
    summary='获取分类树结构'
)
async def get_topic_category_tree(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
):
    """
    获取话题分类树结构
    """
    category_tree_result = await TopicCategoryService.get_category_tree_services(query_db)
    logger.info('获取话题分类树结构成功')

    return ResponseUtil.success(data=category_tree_result)


@topicCategoryController.post(
    '',
    dependencies=[Depends(CheckUserInterfaceAuth('spoken_classification:topic_category:add'))],
    summary='新增分类'
)
@ValidateFields(validate_model='add_topic_category')
@Log(title='话题分类管理', business_type=BusinessType.INSERT)
async def add_topic_category(
    request: Request,
    add_category: TopicCategoryModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    新增话题分类
    """
    add_category.create_by = current_user.user.user_name
    add_category.create_time = datetime.now()
    add_category.update_by = current_user.user.user_name
    add_category.update_time = datetime.now()
    add_category_result = await TopicCategoryService.add_category_services(query_db, add_category)
    logger.info(add_category_result.message)

    return ResponseUtil.success(data=add_category_result)


@topicCategoryController.put(
    '',
    dependencies=[Depends(CheckUserInterfaceAuth('spoken_classification:topic_category:edit'))],
    summary='编辑分类'
)
@ValidateFields(validate_model='edit_topic_category')
@Log(title='话题分类管理', business_type=BusinessType.UPDATE)
async def edit_topic_category(
    request: Request,
    edit_category: TopicCategoryModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    编辑话题分类
    """
    edit_category.update_by = current_user.user.user_name
    edit_category.update_time = datetime.now()
    edit_category_result = await TopicCategoryService.edit_category_services(query_db, edit_category)
    logger.info(edit_category_result.message)

    return ResponseUtil.success(msg=edit_category_result.message)


@topicCategoryController.delete(
    '/{category_ids}',
    dependencies=[Depends(CheckUserInterfaceAuth('spoken_classification:topic_category:remove'))],
    summary='删除分类'
)
@Log(title='话题分类管理', business_type=BusinessType.DELETE)
async def delete_topic_category(
    request: Request,
    category_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    删除话题分类
    """
    delete_category = DeleteTopicCategoryModel(
        category_ids=category_ids,
        update_by=current_user.user.user_name,
        update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    delete_category_result = await TopicCategoryService.delete_category_services(query_db, delete_category)
    logger.info(delete_category_result.message)

    return ResponseUtil.success(msg=delete_category_result.message)