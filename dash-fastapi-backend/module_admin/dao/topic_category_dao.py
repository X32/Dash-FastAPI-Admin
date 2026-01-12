from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from module_admin.entity.do.topic_category_do import SysTopicCategory
from module_admin.entity.do.spoken_topic_do import SysSpokenTopic
from module_admin.entity.vo.topic_category_vo import TopicCategoryModel


class TopicCategoryDao:
    """
    话题分类管理模块数据库操作层
    """

    @classmethod
    async def get_topic_category_by_id(cls, db: AsyncSession, category_id: int):
        """
        根据分类id获取在用分类信息

        :param db: orm对象
        :param category_id: 分类id
        :return: 在用分类信息对象
        """
        category_info = (await db.execute(select(SysTopicCategory).where(SysTopicCategory.category_id == category_id))).scalars().first()

        return category_info

    @classmethod
    async def get_topic_category_detail_by_id(cls, db: AsyncSession, category_id: int):
        """
        根据分类id获取分类详细信息

        :param db: orm对象
        :param category_id: 分类id
        :return: 分类信息对象
        """
        category_info = (
            (await db.execute(select(SysTopicCategory).where(SysTopicCategory.category_id == category_id, SysTopicCategory.del_flag == '0')))
            .scalars()
            .first()
        )

        return category_info

    @classmethod
    async def get_topic_category_detail_by_info(cls, db: AsyncSession, category: TopicCategoryModel):
        """
        根据分类参数获取分类信息

        :param db: orm对象
        :param category: 分类参数对象
        :return: 分类信息对象
        """
        category_info = (
            (
                await db.execute(
                    select(SysTopicCategory).where(
                        SysTopicCategory.parent_id == category.parent_id if category.parent_id else True,
                        SysTopicCategory.category_name == category.category_name if category.category_name else True,
                    )
                )
            )
            .scalars()
            .first()
        )

        return category_info

    @classmethod
    async def get_children_topic_category_dao(cls, db: AsyncSession, category_id: int):
        """
        根据分类id查询当前分类的子分类列表信息

        :param db: orm对象
        :param category_id: 分类id
        :return: 子分类信息列表
        """
        category_result = (
            (await db.execute(select(SysTopicCategory).where(func.find_in_set(category_id, SysTopicCategory.ancestors)))).scalars().all()
        )

        return category_result

    @classmethod
    async def get_topic_category_list_for_tree(cls, db: AsyncSession, category_info: TopicCategoryModel, data_scope_sql: str):
        """
        获取所有在用分类列表信息

        :param db: orm对象
        :param category_info: 分类对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 在用分类列表信息
        """
        category_result = (
            (
                await db.execute(
                    select(SysTopicCategory)
                    .where(
                        SysTopicCategory.status == '0',
                        SysTopicCategory.del_flag == '0',
                        SysTopicCategory.category_name.like(f'%{category_info.category_name}%') if category_info.category_name else True,
                        eval(data_scope_sql),
                    )
                    .order_by(SysTopicCategory.order_num)
                    .distinct()
                )
            )
            .scalars()
            .all()
        )

        return category_result

    @classmethod
    async def get_topic_category_list(cls, db: AsyncSession, page_object: TopicCategoryModel, data_scope_sql: str):
        """
        根据查询参数获取分类列表信息

        :param db: orm对象
        :param page_object: 不分页查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 分类列表信息对象
        """
        category_result = (
            (
                await db.execute(
                    select(SysTopicCategory)
                    .where(
                        SysTopicCategory.del_flag == '0',
                        SysTopicCategory.category_id == page_object.category_id if page_object.category_id is not None else True,
                        SysTopicCategory.status == page_object.status if page_object.status else True,
                        SysTopicCategory.category_name.like(f'%{page_object.category_name}%') if page_object.category_name else True,
                        eval(data_scope_sql),
                    )
                    .order_by(SysTopicCategory.order_num)
                    .distinct()
                )
            )
            .scalars()
            .all()
        )

        return category_result

    @classmethod
    async def add_topic_category_dao(cls, db: AsyncSession, category: TopicCategoryModel):
        """
        新增分类数据库操作

        :param db: orm对象
        :param category: 分类对象
        :return: 新增校验结果
        """
        db_category = SysTopicCategory(**category.model_dump())
        db.add(db_category)
        await db.flush()

        return db_category

    @classmethod
    async def edit_topic_category_dao(cls, db: AsyncSession, category: dict):
        """
        编辑分类数据库操作

        :param db: orm对象
        :param category: 需要更新的分类字典
        :return: 编辑分类校验结果
        """
        await db.execute(update(SysTopicCategory).where(SysTopicCategory.category_id == category.get('category_id')).values(category))
        await db.flush()

    @classmethod
    async def delete_topic_category_dao(cls, db: AsyncSession, category: TopicCategoryModel):
        """
        删除分类数据库操作

        :param db: orm对象
        :param category: 需要删除的分类对象
        :return: 删除分类校验结果
        """
        await db.execute(update(SysTopicCategory).where(SysTopicCategory.category_id.in_(category.category_ids.split(', '))).values(del_flag='2', update_by=category.update_by, update_time=category.update_time))
        await db.flush()


class SpokenTopicDao:
    """
    话题管理模块数据库操作层
    """

    @classmethod
    async def get_spoken_topic_by_id(cls, db: AsyncSession, topic_id: int):
        """
        根据话题id获取在用话题信息

        :param db: orm对象
        :param topic_id: 话题id
        :return: 在用话题信息对象
        """
        topic_info = (await db.execute(select(SysSpokenTopic).where(SysSpokenTopic.topic_id == topic_id))).scalars().first()

        return topic_info

    @classmethod
    async def get_spoken_topic_detail_by_id(cls, db: AsyncSession, topic_id: int):
        """
        根据话题id获取话题详细信息

        :param db: orm对象
        :param topic_id: 话题id
        :return: 话题信息对象
        """
        topic_info = (
            (await db.execute(select(SysSpokenTopic).where(SysSpokenTopic.topic_id == topic_id, SysSpokenTopic.del_flag == '0')))
            .scalars()
            .first()
        )

        return topic_info

    @classmethod
    async def get_spoken_topic_detail_by_info(cls, db: AsyncSession, topic: TopicCategoryModel):
        """
        根据话题参数获取话题信息

        :param db: orm对象
        :param topic: 话题参数对象
        :return: 话题信息对象
        """
        topic_info = (
            (
                await db.execute(
                    select(SysSpokenTopic).where(
                        SysSpokenTopic.category_id == topic.category_id if topic.category_id else True,
                        SysSpokenTopic.topic_name == topic.topic_name if topic.topic_name else True,
                    )
                )
            )
            .scalars()
            .first()
        )

        return topic_info

    @classmethod
    async def get_spoken_topic_list(cls, db: AsyncSession, page_object: TopicCategoryModel, data_scope_sql: str):
        """
        根据查询参数获取话题列表信息

        :param db: orm对象
        :param page_object: 不分页查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 话题列表信息对象
        """
        topic_result = (
            (
                await db.execute(
                    select(SysSpokenTopic)
                    .where(
                        SysSpokenTopic.del_flag == '0',
                        SysSpokenTopic.topic_id == page_object.topic_id if page_object.topic_id is not None else True,
                        SysSpokenTopic.status == page_object.status if page_object.status else True,
                        SysSpokenTopic.topic_name.like(f'%{page_object.topic_name}%') if page_object.topic_name else True,
                        SysSpokenTopic.category_id == page_object.category_id if page_object.category_id else True,
                        eval(data_scope_sql),
                    )
                    .order_by(SysSpokenTopic.create_time.desc())
                    .distinct()
                )
            )
            .scalars()
            .all()
        )

        return topic_result

    @classmethod
    async def get_spoken_topic_count_by_category_id(cls, db: AsyncSession, category_id: int):
        """
        根据分类id获取话题数量

        :param db: orm对象
        :param category_id: 分类id
        :return: 话题数量
        """
        topic_count = (await db.execute(select(func.count(SysSpokenTopic.topic_id)).where(SysSpokenTopic.category_id == category_id, SysSpokenTopic.del_flag == '0'))).scalar()

        return topic_count

    @classmethod
    async def add_spoken_topic_dao(cls, db: AsyncSession, topic: TopicCategoryModel):
        """
        新增话题数据库操作

        :param db: orm对象
        :param topic: 话题对象
        :return: 新增校验结果
        """
        db_topic = SysSpokenTopic(**topic.model_dump())
        db.add(db_topic)
        await db.flush()

        return db_topic

    @classmethod
    async def edit_spoken_topic_dao(cls, db: AsyncSession, topic: dict):
        """
        编辑话题数据库操作

        :param db: orm对象
        :param topic: 需要更新的话题字典
        :return: 编辑话题校验结果
        """
        await db.execute(update(SysSpokenTopic).where(SysSpokenTopic.topic_id == topic.get('topic_id')).values(topic))
        await db.flush()

    @classmethod
    async def delete_spoken_topic_dao(cls, db: AsyncSession, topic: TopicCategoryModel):
        """
        删除话题数据库操作

        :param db: orm对象
        :param topic: 需要删除的话题对象
        :return: 删除话题校验结果
        """
        await db.execute(update(SysSpokenTopic).where(SysSpokenTopic.topic_id.in_(topic.topic_ids.split(', '))).values(del_flag='2', update_by=topic.update_by, update_time=topic.update_time))
        await db.flush()
