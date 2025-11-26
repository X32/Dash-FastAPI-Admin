from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.data_scope import GetDataScope
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.topic_category_vo import (
    DeleteSpokenTopicModel,
    DeleteTopicCategoryModel,
    SpokenTopicModel,
    SpokenTopicPageQueryModel,
    TopicCategoryModel,
    TopicCategoryPageQueryModel,
)
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_admin.service.topic_category_service import SpokenTopicService, TopicCategoryService
from utils.log_util import logger
from utils.response_util import ResponseUtil
from utils.page_util import PageResponseModel


topicCategoryController = APIRouter(prefix='/system', dependencies=[Depends(LoginService.get_current_user)])


@topicCategoryController.get(
    '/topicCategory/tree',
    response_model=List[TopicCategoryModel],
    dependencies=[Depends(CheckUserInterfaceAuth('system:topicCategory:list'))],
)
async def get_system_topic_category_tree(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    data_scope_sql: str = Depends(GetDataScope('SysTopicCategory')),
):
    category_tree_result = await TopicCategoryService.get_topic_category_tree_services(query_db, TopicCategoryModel(), data_scope_sql)
    logger.info('获取成功')

    return ResponseUtil.success(data=category_tree_result)


@topicCategoryController.get(
    '/topicCategory/list', 
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('system:topicCategory:list'))]
)
async def get_system_topic_category_list(
    request: Request,
    category_query: TopicCategoryPageQueryModel = Query(),
    query_db: AsyncSession = Depends(get_db),
    data_scope_sql: str = Depends(GetDataScope('SysTopicCategory')),
):
    category_list_result = await TopicCategoryService.get_topic_category_list_services(query_db, category_query, data_scope_sql, is_page=True)
    logger.info('获取成功')

    return ResponseUtil.success(data=category_list_result)


@topicCategoryController.post('/topicCategory', dependencies=[Depends(CheckUserInterfaceAuth('system:topicCategory:add'))])
@ValidateFields(validate_model='add_topic_category')
@Log(title='话题分类管理', business_type=BusinessType.INSERT)
async def add_system_topic_category(
    request: Request,
    add_category: TopicCategoryModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_category.create_by = current_user.user.user_name
    add_category.create_time = datetime.now()
    add_category.update_by = current_user.user.user_name
    add_category.update_time = datetime.now()
    add_category_result = await TopicCategoryService.add_topic_category_services(query_db, add_category)
    logger.info(add_category_result.message)

    return ResponseUtil.success(data=add_category_result)


@topicCategoryController.put('/topicCategory', dependencies=[Depends(CheckUserInterfaceAuth('system:topicCategory:edit'))])
@ValidateFields(validate_model='edit_topic_category')
@Log(title='话题分类管理', business_type=BusinessType.UPDATE)
async def edit_system_topic_category(
    request: Request,
    edit_category: TopicCategoryModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    data_scope_sql: str = Depends(GetDataScope('SysTopicCategory')),
):
    if not current_user.user.admin:
        await TopicCategoryService.check_topic_category_data_scope_services(query_db, edit_category.category_id, data_scope_sql)
    edit_category.update_by = current_user.user.user_name
    edit_category.update_time = datetime.now()
    edit_category_result = await TopicCategoryService.edit_topic_category_services(query_db, edit_category)
    logger.info(edit_category_result.message)

    return ResponseUtil.success(msg=edit_category_result.message)


@topicCategoryController.delete('/topicCategory/{category_ids}', dependencies=[Depends(CheckUserInterfaceAuth('system:topicCategory:remove'))])
@Log(title='话题分类管理', business_type=BusinessType.DELETE)
async def delete_system_topic_category(
    request: Request,
    category_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    data_scope_sql: str = Depends(GetDataScope('SysTopicCategory')),
):
    category_id_list = category_ids.split(',') if category_ids else []
    if category_id_list:
        for category_id in category_id_list:
            if not current_user.user.admin:
                await TopicCategoryService.check_topic_category_data_scope_services(query_db, int(category_id), data_scope_sql)
    delete_category = DeleteTopicCategoryModel(category_ids=category_ids)
    delete_category.update_by = current_user.user.user_name
    delete_category.update_time = datetime.now()
    delete_category_result = await TopicCategoryService.delete_topic_category_services(query_db, delete_category)
    logger.info(delete_category_result.message)

    return ResponseUtil.success(msg=delete_category_result.message)


@topicCategoryController.get(
    '/topicCategory/{category_id}', 
    response_model=TopicCategoryModel, 
    dependencies=[Depends(CheckUserInterfaceAuth('system:topicCategory:query'))]
)
async def query_detail_system_topic_category(
    request: Request,
    category_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    data_scope_sql: str = Depends(GetDataScope('SysTopicCategory')),
):
    if not current_user.user.admin:
        await TopicCategoryService.check_topic_category_data_scope_services(query_db, category_id, data_scope_sql)
    detail_category_result = await TopicCategoryService.topic_category_detail_services(query_db, category_id)
    logger.info(f'获取category_id为{category_id}的信息成功')

    return ResponseUtil.success(data=detail_category_result)


@topicCategoryController.get(
    '/spokenTopic/list', 
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('system:spokenTopic:list'))]
)
async def get_system_spoken_topic_list(
    request: Request,
    topic_query: SpokenTopicPageQueryModel = Query(),
    query_db: AsyncSession = Depends(get_db),
    data_scope_sql: str = Depends(GetDataScope('SysSpokenTopic')),
):
    topic_list_result = await SpokenTopicService.get_spoken_topic_list_services(query_db, topic_query, data_scope_sql, is_page=True)
    logger.info('获取成功')

    return ResponseUtil.success(data=topic_list_result)


@topicCategoryController.post('/spokenTopic', dependencies=[Depends(CheckUserInterfaceAuth('system:spokenTopic:add'))])
@ValidateFields(validate_model='add_spoken_topic')
@Log(title='话题管理', business_type=BusinessType.INSERT)
async def add_system_spoken_topic(
    request: Request,
    add_topic: SpokenTopicModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_topic.create_by = current_user.user.user_name
    add_topic.create_time = datetime.now()
    add_topic.update_by = current_user.user.user_name
    add_topic.update_time = datetime.now()
    add_topic_result = await SpokenTopicService.add_spoken_topic_services(query_db, add_topic)
    logger.info(add_topic_result.message)

    return ResponseUtil.success(data=add_topic_result)


@topicCategoryController.put('/spokenTopic', dependencies=[Depends(CheckUserInterfaceAuth('system:spokenTopic:edit'))])
@ValidateFields(validate_model='edit_spoken_topic')
@Log(title='话题管理', business_type=BusinessType.UPDATE)
async def edit_system_spoken_topic(
    request: Request,
    edit_topic: SpokenTopicModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    data_scope_sql: str = Depends(GetDataScope('SysSpokenTopic')),
):
    if not current_user.user.admin:
        await SpokenTopicService.check_spoken_topic_data_scope_services(query_db, edit_topic.topic_id, data_scope_sql)
    edit_topic.update_by = current_user.user.user_name
    edit_topic.update_time = datetime.now()
    edit_topic_result = await SpokenTopicService.edit_spoken_topic_services(query_db, edit_topic)
    logger.info(edit_topic_result.message)

    return ResponseUtil.success(msg=edit_topic_result.message)


@topicCategoryController.delete('/spokenTopic/{topic_ids}', dependencies=[Depends(CheckUserInterfaceAuth('system:spokenTopic:remove'))])
@Log(title='话题管理', business_type=BusinessType.DELETE)
async def delete_system_spoken_topic(
    request: Request,
    topic_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    data_scope_sql: str = Depends(GetDataScope('SysSpokenTopic')),
):
    topic_id_list = topic_ids.split(',') if topic_ids else []
    if topic_id_list:
        for topic_id in topic_id_list:
            if not current_user.user.admin:
                await SpokenTopicService.check_spoken_topic_data_scope_services(query_db, int(topic_id), data_scope_sql)
    delete_topic = DeleteSpokenTopicModel(topic_ids=topic_ids)
    delete_topic.update_by = current_user.user.user_name
    delete_topic.update_time = datetime.now()
    delete_topic_result = await SpokenTopicService.delete_spoken_topic_services(query_db, delete_topic)
    logger.info(delete_topic_result.message)

    return ResponseUtil.success(msg=delete_topic_result.message)


@topicCategoryController.get(
    '/spokenTopic/{topic_id}', 
    response_model=SpokenTopicModel, 
    dependencies=[Depends(CheckUserInterfaceAuth('system:spokenTopic:query'))]
)
async def query_detail_system_spoken_topic(
    request: Request,
    topic_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    data_scope_sql: str = Depends(GetDataScope('SysSpokenTopic')),
):
    if not current_user.user.admin:
        await SpokenTopicService.check_spoken_topic_data_scope_services(query_db, topic_id, data_scope_sql)
    detail_topic_result = await SpokenTopicService.spoken_topic_detail_services(query_db, topic_id)
    logger.info(f'获取topic_id为{topic_id}的信息成功')

    return ResponseUtil.success(data=detail_topic_result)
