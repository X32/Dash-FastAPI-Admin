from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request, Query
from starlette.responses import Response
from config.get_db import get_db
from config.get_db import get_db
from utils.response_util import ResponseUtil
from utils.log_util import logger
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.aspect.data_scope import GetDataScope
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.entity.vo.topic_category_vo import TopicCategoryModel, TopicCategoryPageQueryModel, DeleteTopicCategoryModel
from module_admin.service.topic_category_service import TopicCategoryService
from module_admin.service.login_service import LoginService
from module_admin.entity.vo.user_vo import CurrentUserModel


topicCategoryController = APIRouter(prefix='/admin/topicCategory', dependencies=[Depends(get_db)])


@topicCategoryController.get('/list', response_model=TopicCategoryPageQueryModel, dependencies=[Depends(GetDataScope())])
async def get_topic_category_list(
    request: Request,
    category_id: int = Query(None, description='分类ID'),
    parent_id: int = Query(None, description='父分类ID'),
    category_name: str = Query(None, description='分类名称'),
    status: str = Query(None, description='状态'),
    page_num: int = Query(1, description='当前页码'),
    page_size: int = Query(10, description='每页数量'),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    获取话题分类列表
    """
    try:
        query_object = TopicCategoryPageQueryModel(
            category_id=category_id,
            parent_id=parent_id,
            category_name=category_name,
            status=status,
            page_num=page_num,
            page_size=page_size
        )
        
        # 获取数据权限对应的查询sql语句
        data_scope_sql = current_user.get('data_scope_sql', '')
        category_list_result = await TopicCategoryService.get_topic_category_list_services(
            query_db, query_object, data_scope_sql, is_page=True
        )
        
        logger.info('获取话题分类列表成功')
        return ResponseUtil.success(model_content=category_list_result)
    except Exception as e:
        logger.exception('获取话题分类列表失败')
        return ResponseUtil.error(msg=str(e))


@topicCategoryController.post('', dependencies=[Depends(CheckUserInterfaceAuth('admin:topicCategory:add'))])
async def add_topic_category(
    request: Request,
    add_category: TopicCategoryModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    新增话题分类
    """
    try:
        add_category.create_by = current_user.user.user_name
        add_category.create_time = datetime.now()
        add_category.update_by = current_user.user.user_name
        add_category.update_time = datetime.now()
        
        add_result = await TopicCategoryService.add_topic_category_services(query_db, add_category)
        if add_result.is_success:
            logger.info(f'新增话题分类{add_category.category_name}成功')
            return ResponseUtil.success(msg=add_result.message)
        else:
            logger.warning(f'新增话题分类{add_category.category_name}失败：{add_result.message}')
            return ResponseUtil.error(msg=add_result.message)
    except Exception as e:
        logger.exception('新增话题分类失败')
        return ResponseUtil.error(msg=str(e))


@topicCategoryController.put('', dependencies=[Depends(CheckUserInterfaceAuth('admin:topicCategory:edit'))])
async def edit_topic_category(
    request: Request,
    edit_category: TopicCategoryModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    编辑话题分类
    """
    try:
        edit_category.update_by = current_user.user.user_name
        edit_category.update_time = datetime.now()
        
        edit_result = await TopicCategoryService.edit_topic_category_services(query_db, edit_category)
        if edit_result.is_success:
            logger.info(f'编辑话题分类{edit_category.category_name}成功')
            return ResponseUtil.success(msg=edit_result.message)
        else:
            logger.warning(f'编辑话题分类{edit_category.category_name}失败：{edit_result.message}')
            return ResponseUtil.error(msg=edit_result.message)
    except Exception as e:
        logger.exception('编辑话题分类失败')
        return ResponseUtil.error(msg=str(e))


@topicCategoryController.delete('/{category_ids}', dependencies=[Depends(CheckUserInterfaceAuth('admin:topicCategory:remove'))])
async def delete_topic_category(
    request: Request,
    category_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    删除话题分类
    """
    try:
        delete_category = DeleteTopicCategoryModel(
            category_ids=category_ids,
            update_by=current_user.user.user_name,
        update_time=datetime.now()
        )
        
        delete_result = await TopicCategoryService.delete_topic_category_services(query_db, delete_category)
        if delete_result.is_success:
            logger.info(f'删除话题分类成功')
            return ResponseUtil.success(msg=delete_result.message)
        else:
            logger.warning(f'删除话题分类失败：{delete_result.message}')
            return ResponseUtil.error(msg=delete_result.message)
    except Exception as e:
        logger.exception('删除话题分类失败')
        return ResponseUtil.error(msg=str(e))


@topicCategoryController.get('/{category_id}')
async def get_topic_category_detail(
    request: Request,
    category_id: int,
    query_db: AsyncSession = Depends(get_db)
):
    """
    获取话题分类详细信息
    """
    try:
        category_detail = await TopicCategoryService.get_topic_category_detail_services(query_db, category_id)
        logger.info(f'获取话题分类{category_id}详细信息成功')
        return ResponseUtil.success(data=category_detail)
    except Exception as e:
        logger.exception(f'获取话题分类{category_id}详细信息失败')
        return ResponseUtil.error(msg=str(e))


@topicCategoryController.get('/treeSelect', response_model=List[dict])
async def get_topic_category_tree(
    request: Request,
    query_db: AsyncSession = Depends(get_db)
):
    """
    获取话题分类树形结构
    """
    try:
        category_tree = await TopicCategoryService.get_topic_category_tree_services(query_db)
        logger.info('获取话题分类树形结构成功')
        return ResponseUtil.success(data=category_tree)
    except Exception as e:
        logger.exception('获取话题分类树形结构失败')
        return ResponseUtil.error(msg=str(e))


@topicCategoryController.get('/optionselect', response_model=List[dict])
async def get_topic_category_option(
    request: Request,
    query_db: AsyncSession = Depends(get_db)
):
    """
    获取话题分类选择框列表
    """
    try:
        category_option = await TopicCategoryService.get_topic_category_option_services(query_db)
        logger.info('获取话题分类选择框列表成功')
        return ResponseUtil.success(data=category_option)
    except Exception as e:
        logger.exception('获取话题分类选择框列表失败')
        return ResponseUtil.error(msg=str(e))