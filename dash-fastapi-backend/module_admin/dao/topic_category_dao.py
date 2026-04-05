from sqlalchemy import delete, func, select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.topic_category_do import SysTopicCategory
from module_admin.entity.do.topic_do import SysSpeakingTopic
from module_admin.entity.vo.topic_category_vo import TopicCategoryModel, TopicCategoryPageQueryModel
from utils.page_util import PageUtil


class TopicCategoryDao:
    """
    话题分类管理模块数据库操作层
    """

    @classmethod
    async def get_topic_category_list(cls, db: AsyncSession, query_object: TopicCategoryPageQueryModel, is_page: bool = False):
        """
        获取话题分类列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 话题分类列表信息对象
        """
        query = select(SysTopicCategory).where(SysTopicCategory.del_flag == '0')
        
        # 根据分类名称模糊查询
        if query_object.category_name:
            query = query.where(SysTopicCategory.category_name.like(f'%{query_object.category_name}%'))
        
        # 根据状态查询
        if query_object.status:
            query = query.where(SysTopicCategory.status == query_object.status)
        
        # 根据父分类id查询
        if query_object.parent_id is not None:
            query = query.where(SysTopicCategory.parent_id == query_object.parent_id)
        
        # 根据创建时间范围查询
        if query_object.begin_time and query_object.end_time:
            query = query.where(
                and_(
                    SysTopicCategory.create_time >= query_object.begin_time,
                    SysTopicCategory.create_time <= query_object.end_time
                )
            )
        
        # 排序
        query = query.order_by(SysTopicCategory.parent_id, SysTopicCategory.order_num, SysTopicCategory.category_id)
        
        # 分页查询
        if is_page:
            return await PageUtil.paginate(query, query_object.page_num, query_object.page_size)
        
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_topic_category_by_id(cls, db: AsyncSession, category_id: int):
        """
        根据分类id获取分类详细信息

        :param db: orm对象
        :param category_id: 分类id
        :return: 分类信息对象
        """
        query = select(SysTopicCategory).where(SysTopicCategory.category_id == category_id, SysTopicCategory.del_flag == '0')
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def add_topic_category_dao(cls, db: AsyncSession, category: TopicCategoryModel):
        """
        新增话题分类数据库操作

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
        编辑话题分类数据库操作

        :param db: orm对象
        :param category: 需要更新的分类字典
        :return:
        """
        await db.execute(update(SysTopicCategory), [category])

    @classmethod
    async def delete_topic_category_dao(cls, db: AsyncSession, category: dict):
        """
        删除话题分类数据库操作

        :param db: orm对象
        :param category: 需要删除的分类字典
        :return:
        """
        await db.execute(update(SysTopicCategory), [category])

    @classmethod
    async def check_category_name_unique(cls, db: AsyncSession, category: TopicCategoryModel):
        """
        校验分类名称是否唯一

        :param db: orm对象
        :param category: 分类对象
        :return: 分类名称是否唯一
        """
        category_id = -1 if category.category_id is None else category.category_id
        query = select(func.count()).where(
            SysTopicCategory.category_name == category.category_name,
            SysTopicCategory.del_flag == '0',
            SysTopicCategory.category_id != category_id
        )
        result = await db.execute(query)
        count = result.scalar()
        
        return count == 0

    @classmethod
    async def count_child_categories(cls, db: AsyncSession, parent_id: int):
        """
        根据父分类id查询子分类数量

        :param db: orm对象
        :param parent_id: 父分类id
        :return: 子分类数量
        """
        query = select(func.count()).where(
            SysTopicCategory.parent_id == parent_id,
            SysTopicCategory.del_flag == '0'
        )
        result = await db.execute(query)
        return result.scalar()

    @classmethod
    async def count_topics_by_category(cls, db: AsyncSession, category_id: int):
        """
        根据分类id查询关联的话题数量

        :param db: orm对象
        :param category_id: 分类id
        :return: 关联的话题数量
        """
        query = select(func.count()).where(
            SysSpeakingTopic.category_id == category_id,
            SysSpeakingTopic.del_flag == '0'
        )
        result = await db.execute(query)
        return result.scalar()

    @classmethod
    async def get_all_parent_categories(cls, db: AsyncSession):
        """
        获取所有父分类（一级分类）列表

        :param db: orm对象
        :return: 父分类列表
        """
        query = select(SysTopicCategory).where(
            SysTopicCategory.parent_id == 0,
            SysTopicCategory.del_flag == '0',
            SysTopicCategory.status == '0'
        ).order_by(SysTopicCategory.order_num, SysTopicCategory.category_id)
        
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_children_categories(cls, db: AsyncSession, parent_id: int):
        """
        获取指定父分类的子分类列表

        :param db: orm对象
        :param parent_id: 父分类id
        :return: 子分类列表
        """
        query = select(SysTopicCategory).where(
            SysTopicCategory.parent_id == parent_id,
            SysTopicCategory.del_flag == '0',
            SysTopicCategory.status == '0'
        ).order_by(SysTopicCategory.order_num, SysTopicCategory.category_id)
        
        result = await db.execute(query)
        return result.scalars().all()