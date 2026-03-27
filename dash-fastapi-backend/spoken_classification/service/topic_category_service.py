from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from config.constant import CommonConstant
from exceptions.exception import ServiceException, ServiceWarning
from spoken_classification.dao.topic_category_dao import TopicCategoryDao
from spoken_classification.entity.vo.common_vo import CrudResponseModel
from spoken_classification.entity.vo.topic_category_vo import (
    DeleteTopicCategoryModel,
    TopicCategoryModel,
)
from utils.common_util import SqlalchemyUtil


class TopicCategoryService:
    """
    话题分类管理模块服务层
    """

    @classmethod
    async def get_first_level_categories_services(cls, query_db: AsyncSession):
        """
        获取一级分类列表service

        :param query_db: orm对象
        :return: 一级分类列表信息对象
        """
        category_list_result = await TopicCategoryDao.get_first_level_categories(query_db)

        return SqlalchemyUtil.serialize_result(category_list_result)

    @classmethod
    async def get_second_level_categories_services(cls, query_db: AsyncSession, parent_id: int):
        """
        获取指定一级分类下的二级分类列表service

        :param query_db: orm对象
        :param parent_id: 父分类ID
        :return: 二级分类列表信息对象
        """
        # 检查父分类是否存在
        parent_category = await TopicCategoryDao.get_category_detail_by_id(query_db, parent_id)
        if not parent_category:
            raise ServiceException(message='父分类不存在')
        if parent_category.parent_id != 0:
            raise ServiceException(message='只能查询一级分类下的二级分类')

        category_list_result = await TopicCategoryDao.get_second_level_categories(query_db, parent_id)

        return SqlalchemyUtil.serialize_result(category_list_result)

    @classmethod
    async def get_category_tree_services(cls, query_db: AsyncSession):
        """
        获取分类树信息service

        :param query_db: orm对象
        :return: 分类树信息对象
        """
        category_list_result = await TopicCategoryDao.get_all_categories(query_db)
        category_tree_result = cls.list_to_tree(category_list_result)

        return category_tree_result

    @classmethod
    def list_to_tree(cls, data: list) -> list:
        """
        列表转树结构

        :param data: 列表数据
        :return: 树结构数据
        """
        result = []
        temp = {}

        for item in data:
            item_dict = SqlalchemyUtil.serialize_result(item)
            item_dict['children'] = []
            temp[item_dict['category_id']] = item_dict

        for item in data:
            item_dict = SqlalchemyUtil.serialize_result(item)
            if item_dict['parent_id'] != 0 and item_dict['parent_id'] in temp:
                temp[item_dict['parent_id']]['children'].append(item_dict)
            else:
                result.append(item_dict)

        return result

    @classmethod
    async def check_category_name_unique_services(cls, query_db: AsyncSession, page_object: TopicCategoryModel):
        """
        校验分类名称是否唯一service

        :param query_db: orm对象
        :param page_object: 分类对象
        :return: 校验结果
        """
        category_id = -1 if page_object.category_id is None else page_object.category_id
        category = await TopicCategoryDao.get_category_detail_by_info(
            query_db, TopicCategoryModel(category_name=page_object.category_name, parent_id=page_object.parent_id)
        )
        if category and category.category_id != category_id:
            return CommonConstant.NOT_UNIQUE
        return CommonConstant.UNIQUE

    @classmethod
    async def add_category_services(cls, query_db: AsyncSession, page_object: TopicCategoryModel):
        """
        新增分类信息service

        :param query_db: orm对象
        :param page_object: 新增分类对象
        :return: 新增分类校验结果
        """
        # 校验分类名称是否唯一
        unique_result = await cls.check_category_name_unique_services(query_db, page_object)
        if unique_result == CommonConstant.NOT_UNIQUE:
            raise ServiceException(message='同一父分类下分类名称不能重复')

        # 如果是二级分类，检查父分类是否存在
        if page_object.parent_id and page_object.parent_id != 0:
            parent_category = await TopicCategoryDao.get_category_detail_by_id(query_db, page_object.parent_id)
            if not parent_category:
                raise ServiceException(message='父分类不存在')

        await TopicCategoryDao.add_category(query_db, page_object)
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='新增成功')

    @classmethod
    async def edit_category_services(cls, query_db: AsyncSession, page_object: TopicCategoryModel):
        """
        编辑分类信息service

        :param query_db: orm对象
        :param page_object: 编辑分类对象
        :return: 编辑分类校验结果
        """
        # 检查分类是否存在
        category_info = await TopicCategoryDao.get_category_detail_by_id(query_db, page_object.category_id)
        if not category_info:
            raise ServiceException(message='分类不存在')

        # 校验分类名称是否唯一
        unique_result = await cls.check_category_name_unique_services(query_db, page_object)
        if unique_result == CommonConstant.NOT_UNIQUE:
            raise ServiceException(message='同一父分类下分类名称不能重复')

        # 如果是修改父分类，检查新父分类是否存在
        if page_object.parent_id != category_info.parent_id:
            if page_object.parent_id != 0:
                parent_category = await TopicCategoryDao.get_category_detail_by_id(query_db, page_object.parent_id)
                if not parent_category:
                    raise ServiceException(message='新父分类不存在')

        await TopicCategoryDao.update_category(query_db, page_object)
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='更新成功')

    @classmethod
    async def delete_category_services(cls, query_db: AsyncSession, page_object: DeleteTopicCategoryModel):
        """
        删除分类信息service

        :param query_db: orm对象
        :param page_object: 删除分类对象
        :return: 删除分类校验结果
        """
        category_ids = list(map(int, page_object.category_ids.split(',')))

        for category_id in category_ids:
            # 检查分类是否存在
            category_info = await TopicCategoryDao.get_category_detail_by_id(query_db, category_id)
            if not category_info:
                raise ServiceException(message=f'分类ID {category_id} 不存在')

            # 检查是否有子分类
            has_children = await TopicCategoryDao.check_has_children(query_db, category_id)
            if has_children:
                raise ServiceException(message=f'分类ID {category_id} 下存在子分类，无法删除')

            # TODO: 检查是否有关联话题
            # has_topics = await TopicCategoryDao.check_has_topics(query_db, category_id)
            # if has_topics:
            #     raise ServiceException(message=f'分类ID {category_id} 下存在关联话题，无法删除')

        await TopicCategoryDao.delete_category(
            query_db, category_ids, page_object.update_by, page_object.update_time
        )
        await query_db.commit()

        return CrudResponseModel(is_success=True, message='删除成功')