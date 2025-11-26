from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.constant import CommonConstant
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.entity.vo.topic_category_vo import TopicCategoryModel, TopicCategoryPageQueryModel, DeleteTopicCategoryModel
from module_admin.dao.topic_category_dao import TopicCategoryDao
from utils.common_util import SqlalchemyUtil
from utils.page_util import PageResponseModel


class TopicCategoryService:
    """
    话题分类管理模块服务层
    """

    @classmethod
    async def get_topic_category_list_services(
        cls, query_db: AsyncSession, query_object: TopicCategoryPageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        """
        获取话题分类列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 话题分类列表信息对象
        """
        category_list_result = await TopicCategoryDao.get_topic_category_list(query_db, query_object, is_page)
        
        if is_page:
            return PageResponseModel(
                rows=SqlalchemyUtil.serialize_result(category_list_result),
                total=len(category_list_result) if isinstance(category_list_result, list) else category_list_result.total
            )
        else:
            return SqlalchemyUtil.serialize_result(category_list_result)

    @classmethod
    async def get_topic_category_detail_services(cls, query_db: AsyncSession, category_id: int):
        """
        获取话题分类详细信息service

        :param query_db: orm对象
        :param category_id: 分类id
        :return: 分类详细信息对象
        """
        category = await TopicCategoryDao.get_topic_category_by_id(query_db, category_id=category_id)
        if category:
            result = TopicCategoryModel(**SqlalchemyUtil.serialize_result(category))
        else:
            result = TopicCategoryModel(**dict())
        
        return result

    @classmethod
    async def add_topic_category_services(cls, query_db: AsyncSession, page_object: TopicCategoryModel):
        """
        新增话题分类信息service

        :param query_db: orm对象
        :param page_object: 新增分类对象
        :return: 新增分类校验结果
        """
        if not await cls.check_category_name_unique_services(query_db, page_object):
            raise ServiceException(message=f'新增分类{page_object.category_name}失败，分类名称已存在')
        
        # 如果父分类不是根节点，检查父分类是否存在且正常
        if page_object.parent_id != 0:
            parent_info = await TopicCategoryDao.get_topic_category_by_id(query_db, page_object.parent_id)
            if not parent_info:
                raise ServiceException(message=f'新增分类失败，父分类不存在')
            if parent_info.status != CommonConstant.DEPT_NORMAL:
                raise ServiceException(message=f'分类{parent_info.category_name}停用，不允许新增子分类')
        
        try:
            await TopicCategoryDao.add_topic_category_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_topic_category_services(cls, query_db: AsyncSession, page_object: TopicCategoryModel):
        """
        编辑话题分类信息service

        :param query_db: orm对象
        :param page_object: 编辑分类对象
        :return: 编辑分类校验结果
        """
        edit_category = page_object.model_dump(exclude_unset=True)
        category_info = await cls.get_topic_category_detail_services(query_db, page_object.category_id)
        if category_info:
            if not await cls.check_category_name_unique_services(query_db, page_object):
                raise ServiceException(message=f'修改分类{page_object.category_name}失败，分类名称已存在')
            
            # 如果修改了父分类，检查新的父分类是否存在且正常
            if page_object.parent_id is not None and page_object.parent_id != category_info.parent_id:
                if page_object.parent_id != 0:
                    parent_info = await TopicCategoryDao.get_topic_category_by_id(query_db, page_object.parent_id)
                    if not parent_info:
                        raise ServiceException(message=f'修改分类失败，父分类不存在')
                    if parent_info.status != CommonConstant.DEPT_NORMAL:
                        raise ServiceException(message=f'分类{parent_info.category_name}停用，不允许修改为该分类的子分类')
            
            try:
                await TopicCategoryDao.edit_topic_category_dao(query_db, edit_category)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='分类不存在')

    @classmethod
    async def delete_topic_category_services(cls, query_db: AsyncSession, page_object: DeleteTopicCategoryModel):
        """
        删除话题分类信息service

        :param query_db: orm对象
        :param page_object: 删除分类对象
        :return: 删除分类校验结果
        """
        category_ids = page_object.category_ids.split(',') if page_object.category_ids else []
        if category_ids:
            for category_id in category_ids:
                category_info = await cls.get_topic_category_detail_services(query_db, int(category_id))
                if category_info:
                    # 检查是否有子分类
                    child_count = await TopicCategoryDao.count_child_categories(query_db, int(category_id))
                    if child_count > 0:
                        raise ServiceException(message=f'分类{category_info.category_name}存在子分类，不允许删除')
                    
                    # 检查是否有关联的话题
                    topic_count = await TopicCategoryDao.count_topics_by_category(query_db, int(category_id))
                    if topic_count > 0:
                        raise ServiceException(message=f'分类{category_info.category_name}存在关联话题，不允许删除')
                else:
                    raise ServiceException(message='分类不存在')
            
            try:
                for category_id in category_ids:
                    delete_category = dict()
                    delete_category['category_id'] = int(category_id)
                    delete_category['update_by'] = page_object.update_by
                    delete_category['update_time'] = page_object.update_time
                    delete_category['del_flag'] = '2'
                    await TopicCategoryDao.delete_topic_category_dao(query_db, delete_category)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='需要删除的分类id不能为空')

    @classmethod
    async def check_category_name_unique_services(cls, query_db: AsyncSession, page_object: TopicCategoryModel):
        """
        校验分类名称是否唯一service

        :param query_db: orm对象
        :param page_object: 分类对象
        :return: 分类名称是否唯一
        """
        return await TopicCategoryDao.check_category_name_unique(query_db, page_object)

    @classmethod
    async def get_topic_category_tree_services(cls, query_db: AsyncSession):
        """
        获取话题分类树形结构service

        :param query_db: orm对象
        :return: 分类树形结构列表
        """
        # 获取所有一级分类
        parent_categories = await TopicCategoryDao.get_all_parent_categories(query_db)
        
        # 构建树形结构
        tree_list = []
        for parent in parent_categories:
            parent_dict = SqlalchemyUtil.serialize_result(parent)
            # 获取子分类
            children = await TopicCategoryDao.get_children_categories(query_db, parent.category_id)
            parent_dict['children'] = SqlalchemyUtil.serialize_result(children)
            tree_list.append(parent_dict)
        
        return tree_list

    @classmethod
    async def get_topic_category_option_services(cls, query_db: AsyncSession):
        """
        获取话题分类选择框列表service

        :param query_db: orm对象
        :return: 分类选择框列表
        """
        # 获取所有正常状态的分类
        query_object = TopicCategoryPageQueryModel(status='0')
        category_list = await TopicCategoryDao.get_topic_category_list(query_db, query_object)
        
        return SqlalchemyUtil.serialize_result(category_list)