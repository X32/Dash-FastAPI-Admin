from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.constant import CommonConstant
from exceptions.exception import ServiceException, ServiceWarning
from module_admin.dao.topic_category_dao import SpokenTopicDao, TopicCategoryDao
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.entity.vo.topic_category_vo import (
    DeleteSpokenTopicModel,
    DeleteTopicCategoryModel,
    SpokenTopicModel,
    SpokenTopicPageQueryModel,
    TopicCategoryModel,
    TopicCategoryPageQueryModel,
)
from utils.common_util import SqlalchemyUtil
from utils.page_util import PageResponseModel


class TopicCategoryService:
    """
    话题分类管理模块服务层
    """

    @classmethod
    async def get_topic_category_tree_services(cls, query_db: AsyncSession, page_object: TopicCategoryModel, data_scope_sql: str):
        """
        获取话题分类树信息service

        :param query_db: orm对象
        :param page_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 话题分类树信息对象
        """
        category_list_result = await TopicCategoryDao.get_topic_category_list_for_tree(query_db, page_object, data_scope_sql)
        category_tree_result = cls.list_to_tree(category_list_result)

        return category_tree_result

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
        category_list_result = await TopicCategoryDao.get_topic_category_list(query_db, query_object, data_scope_sql)

        return category_list_result

    @classmethod
    async def check_topic_category_data_scope_services(cls, query_db: AsyncSession, category_id: int, data_scope_sql: str):
        """
        校验话题分类是否有数据权限service

        :param query_db: orm对象
        :param category_id: 分类id
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 校验结果
        """
        categories = await TopicCategoryDao.get_topic_category_list(query_db, TopicCategoryModel(category_id=category_id), data_scope_sql)
        if categories:
            return CrudResponseModel(is_success=True, message='校验通过')
        else:
            raise ServiceException(message='没有权限访问分类数据')

    @classmethod
    async def check_topic_category_name_unique_services(cls, query_db: AsyncSession, page_object: TopicCategoryModel):
        """
        校验话题分类名称是否唯一service

        :param query_db: orm对象
        :param page_object: 分类对象
        :return: 校验结果
        """
        category_id = -1 if page_object.category_id is None else page_object.category_id
        category = await TopicCategoryDao.get_topic_category_detail_by_info(
            query_db, TopicCategoryModel(category_name=page_object.category_name, parent_id=page_object.parent_id)
        )
        if category and category.category_id != category_id:
            return CommonConstant.NOT_UNIQUE
        return CommonConstant.UNIQUE

    @classmethod
    async def add_topic_category_services(cls, query_db: AsyncSession, page_object: TopicCategoryModel):
        """
        新增话题分类信息service

        :param query_db: orm对象
        :param page_object: 新增分类对象
        :return: 新增分类校验结果
        """
        if not await cls.check_topic_category_name_unique_services(query_db, page_object):
            raise ServiceException(message=f'新增分类{page_object.category_name}失败，分类名称已存在')
        if page_object.parent_id != 0:
            parent_info = await TopicCategoryDao.get_topic_category_by_id(query_db, page_object.parent_id)
            if parent_info.status != CommonConstant.DEPT_NORMAL:
                raise ServiceException(message=f'分类{parent_info.category_name}停用，不允许新增')
            page_object.ancestors = f'{parent_info.ancestors},{page_object.parent_id}'
        else:
            page_object.ancestors = '0'
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
        if not await cls.check_topic_category_name_unique_services(query_db, page_object):
            raise ServiceException(message=f'修改分类{page_object.category_name}失败，分类名称已存在')
        elif page_object.category_id == page_object.parent_id:
            raise ServiceException(message=f'修改分类{page_object.category_name}失败，上级分类不能是自己')
        new_parent_category = await TopicCategoryDao.get_topic_category_by_id(query_db, page_object.parent_id)
        old_category = await TopicCategoryDao.get_topic_category_by_id(query_db, page_object.category_id)
        try:
            if new_parent_category and old_category:
                new_ancestors = f'{new_parent_category.ancestors},{new_parent_category.category_id}'
                old_ancestors = old_category.ancestors
                page_object.ancestors = new_ancestors
                await cls.update_topic_category_children(query_db, page_object.category_id, new_ancestors, old_ancestors)
            edit_category = page_object.model_dump(exclude_unset=True)
            await TopicCategoryDao.edit_topic_category_dao(query_db, edit_category)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_topic_category_services(cls, query_db: AsyncSession, page_object: DeleteTopicCategoryModel):
        """
        删除话题分类信息service

        :param query_db: orm对象
        :param page_object: 删除分类对象
        :return: 删除分类校验结果
        """
        if page_object.category_ids:
            category_id_list = page_object.category_ids.split(',')
            try:
                for category_id in category_id_list:
                    # 检查是否有子分类
                    children_count = len(await TopicCategoryDao.get_children_topic_category_dao(query_db, int(category_id)))
                    if children_count > 0:
                        raise ServiceWarning(message='存在下级分类,不允许删除')
                    # 检查是否有话题使用该分类
                    topic_count = await SpokenTopicDao.get_spoken_topic_count_by_category_id(query_db, int(category_id))
                    if topic_count > 0:
                        raise ServiceWarning(message='分类存在话题,不允许删除')

                    await TopicCategoryDao.delete_topic_category_dao(query_db, TopicCategoryModel(category_id=category_id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入分类id为空')

    @classmethod
    async def topic_category_detail_services(cls, query_db: AsyncSession, category_id: int):
        """
        获取话题分类详细信息service

        :param query_db: orm对象
        :param category_id: 分类id
        :return: 分类id对应的信息
        """
        category = await TopicCategoryDao.get_topic_category_detail_by_id(query_db, category_id=category_id)
        if category:
            result = TopicCategoryModel(**SqlalchemyUtil.serialize_result(category))
        else:
            result = TopicCategoryModel(**dict())

        return result

    @classmethod
    def list_to_tree(cls, permission_list: list) -> list:
        """
        工具方法：根据分类列表信息生成树形嵌套数据

        :param permission_list: 分类列表信息
        :return: 分类树形嵌套数据
        """
        permission_list = [
            dict(key=str(item.category_id), title=item.category_name, value=str(item.category_id), parent_id=str(item.parent_id))
            for item in permission_list
        ]
        # 转成id为key的字典
        mapping: dict = dict(zip([i['key'] for i in permission_list], permission_list))

        # 树容器
        container: list = []

        for d in permission_list:
            # 如果找不到父级项，则是根节点
            parent: dict = mapping.get(d['parent_id'])
            if parent is None:
                container.append(d)
            else:
                children: list = parent.get('children')
                if not children:
                    children = []
                children.append(d)
                parent.update({'children': children})

        return container

    @classmethod
    async def replace_first(cls, original_str: str, old_str: str, new_str: str):
        """
        工具方法：替换字符串

        :param original_str: 需要替换的原始字符串
        :param old_str: 用于匹配的字符串
        :param new_str: 替换的字符串
        :return: 替换后的字符串
        """
        if original_str.startswith(old_str):
            return original_str.replace(old_str, new_str, 1)
        else:
            return original_str

    @classmethod
    async def update_topic_category_children(cls, query_db: AsyncSession, category_id: int, new_ancestors: str, old_ancestors: str):
        """
        更新子分类信息

        :param query_db: orm对象
        :param category_id: 分类id
        :param new_ancestors: 新的祖先
        :param old_ancestors: 旧的祖先
        :return:
        """
        children = await TopicCategoryDao.get_children_topic_category_dao(query_db, category_id)
        update_children = []
        for child in children:
            child_ancestors = await cls.replace_first(child.ancestors, old_ancestors, new_ancestors)
            update_children.append({'category_id': child.category_id, 'ancestors': child_ancestors})
        if children:
            await TopicCategoryDao.edit_topic_category_dao(query_db, update_children)


class SpokenTopicService:
    """
    话题管理模块服务层
    """

    @classmethod
    async def get_spoken_topic_list_services(
        cls, query_db: AsyncSession, query_object: SpokenTopicPageQueryModel, data_scope_sql: str, is_page: bool = False
    ):
        """
        获取话题列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 话题列表信息对象
        """
        topic_list_result = await SpokenTopicDao.get_spoken_topic_list(query_db, query_object, data_scope_sql)

        return topic_list_result

    @classmethod
    async def check_spoken_topic_data_scope_services(cls, query_db: AsyncSession, topic_id: int, data_scope_sql: str):
        """
        校验话题是否有数据权限service

        :param query_db: orm对象
        :param topic_id: 话题id
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 校验结果
        """
        topics = await SpokenTopicDao.get_spoken_topic_list(query_db, SpokenTopicModel(topic_id=topic_id), data_scope_sql)
        if topics:
            return CrudResponseModel(is_success=True, message='校验通过')
        else:
            raise ServiceException(message='没有权限访问话题数据')

    @classmethod
    async def check_spoken_topic_name_unique_services(cls, query_db: AsyncSession, page_object: SpokenTopicModel):
        """
        校验话题名称是否唯一service

        :param query_db: orm对象
        :param page_object: 话题对象
        :return: 校验结果
        """
        topic_id = -1 if page_object.topic_id is None else page_object.topic_id
        topic = await SpokenTopicDao.get_spoken_topic_detail_by_info(
            query_db, SpokenTopicModel(topic_name=page_object.topic_name, category_id=page_object.category_id)
        )
        if topic and topic.topic_id != topic_id:
            return CommonConstant.NOT_UNIQUE
        return CommonConstant.UNIQUE

    @classmethod
    async def add_spoken_topic_services(cls, query_db: AsyncSession, page_object: SpokenTopicModel):
        """
        新增话题信息service

        :param query_db: orm对象
        :param page_object: 新增话题对象
        :return: 新增话题校验结果
        """
        if not await cls.check_spoken_topic_name_unique_services(query_db, page_object):
            raise ServiceException(message=f'新增话题{page_object.topic_name}失败，话题名称已存在')
        category_info = await TopicCategoryDao.get_topic_category_by_id(query_db, page_object.category_id)
        if category_info.status != CommonConstant.DEPT_NORMAL:
            raise ServiceException(message=f'分类{category_info.category_name}停用，不允许新增话题')
        try:
            await SpokenTopicDao.add_spoken_topic_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_spoken_topic_services(cls, query_db: AsyncSession, page_object: SpokenTopicModel):
        """
        编辑话题信息service

        :param query_db: orm对象
        :param page_object: 编辑话题对象
        :return: 编辑话题校验结果
        """
        if not await cls.check_spoken_topic_name_unique_services(query_db, page_object):
            raise ServiceException(message=f'修改话题{page_object.topic_name}失败，话题名称已存在')
        edit_topic = page_object.model_dump(exclude_unset=True)
        try:
            await SpokenTopicDao.edit_spoken_topic_dao(query_db, edit_topic)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_spoken_topic_services(cls, query_db: AsyncSession, page_object: DeleteSpokenTopicModel):
        """
        删除话题信息service

        :param query_db: orm对象
        :param page_object: 删除话题对象
        :return: 删除话题校验结果
        """
        if page_object.topic_ids:
            topic_id_list = page_object.topic_ids.split(',')
            try:
                for topic_id in topic_id_list:
                    await SpokenTopicDao.delete_spoken_topic_dao(query_db, SpokenTopicModel(topic_id=topic_id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入话题id为空')

    @classmethod
    async def spoken_topic_detail_services(cls, query_db: AsyncSession, topic_id: int):
        """
        获取话题详细信息service

        :param query_db: orm对象
        :param topic_id: 话题id
        :return: 话题id对应的信息
        """
        topic = await SpokenTopicDao.get_spoken_topic_detail_by_id(query_db, topic_id=topic_id)
        if topic:
            result = SpokenTopicModel(**SqlalchemyUtil.serialize_result(topic))
        else:
            result = SpokenTopicModel(**dict())

        return result
