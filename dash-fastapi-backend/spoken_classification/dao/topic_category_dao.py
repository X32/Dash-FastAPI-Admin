from datetime import datetime
from sqlalchemy import func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from spoken_classification.entity.do.topic_category_do import TopicCategory
from spoken_classification.entity.vo.topic_category_vo import TopicCategoryModel, TopicCategoryQueryModel


class TopicCategoryDao:
    """
    话题分类管理模块数据库操作层
    """

    @classmethod
    async def get_category_by_id(cls, db: AsyncSession, category_id: int) -> Optional[TopicCategory]:
        """
        根据分类ID获取分类信息

        :param db: orm对象
        :param category_id: 分类ID
        :return: 分类信息对象
        """
        category_info = (
            await db.execute(select(TopicCategory).where(TopicCategory.category_id == category_id))
        ).scalars().first()

        return category_info

    @classmethod
    async def get_category_detail_by_id(cls, db: AsyncSession, category_id: int) -> Optional[TopicCategory]:
        """
        根据分类ID获取在用分类详细信息

        :param db: orm对象
        :param category_id: 分类ID
        :return: 分类信息对象
        """
        category_info = (
            await db.execute(
                select(TopicCategory).where(
                    TopicCategory.category_id == category_id, TopicCategory.del_flag == '0'
                )
            )
        ).scalars().first()

        return category_info

    @classmethod
    async def get_category_by_parent_id(cls, db: AsyncSession, parent_id: int) -> List[TopicCategory]:
        """
        根据父分类ID获取分类列表

        :param db: orm对象
        :param parent_id: 父分类ID
        :return: 分类列表
        """
        category_list = (
            await db.execute(
                select(TopicCategory)
                .where(TopicCategory.parent_id == parent_id, TopicCategory.del_flag == '0')
                .order_by(TopicCategory.order_num)
            )
        ).scalars().all()

        return category_list

    @classmethod
    async def get_category_detail_by_info(
        cls, db: AsyncSession, category: TopicCategoryModel
    ) -> Optional[TopicCategory]:
        """
        根据分类参数获取分类信息

        :param db: orm对象
        :param category: 分类参数对象
        :return: 分类信息对象
        """
        category_info = (
            await db.execute(
                select(TopicCategory).where(
                    TopicCategory.parent_id == category.parent_id if category.parent_id else True,
                    TopicCategory.category_name == category.category_name if category.category_name else True,
                )
            )
        ).scalars().first()

        return category_info

    @classmethod
    async def get_first_level_categories(cls, db: AsyncSession) -> List[TopicCategory]:
        """
        获取所有一级分类列表

        :param db: orm对象
        :return: 一级分类列表
        """
        category_list = (
            await db.execute(
                select(TopicCategory)
                .where(TopicCategory.parent_id == 0, TopicCategory.del_flag == '0')
                .order_by(TopicCategory.order_num)
            )
        ).scalars().all()

        return category_list

    @classmethod
    async def get_second_level_categories(
        cls, db: AsyncSession, parent_id: int
    ) -> List[TopicCategory]:
        """
        获取指定一级分类下的二级分类列表

        :param db: orm对象
        :param parent_id: 父分类ID
        :return: 二级分类列表
        """
        category_list = (
            await db.execute(
                select(TopicCategory)
                .where(TopicCategory.parent_id == parent_id, TopicCategory.del_flag == '0')
                .order_by(TopicCategory.order_num)
            )
        ).scalars().all()

        return category_list

    @classmethod
    async def get_all_categories(cls, db: AsyncSession) -> List[TopicCategory]:
        """
        获取所有分类列表

        :param db: orm对象
        :return: 分类列表
        """
        category_list = (
            await db.execute(
                select(TopicCategory)
                .where(TopicCategory.del_flag == '0')
                .order_by(TopicCategory.parent_id, TopicCategory.order_num)
            )
        ).scalars().all()

        return category_list

    @classmethod
    async def check_has_children(cls, db: AsyncSession, category_id: int) -> bool:
        """
        检查分类是否有子分类

        :param db: orm对象
        :param category_id: 分类ID
        :return: 是否有子分类
        """
        count = (
            await db.execute(
                select(func.count(TopicCategory.category_id)).where(
                    TopicCategory.parent_id == category_id, TopicCategory.del_flag == '0'
                )
            )
        ).scalar()

        return count > 0

    @classmethod
    async def add_category(cls, db: AsyncSession, category: TopicCategoryModel) -> None:
        """
        新增分类信息

        :param db: orm对象
        :param category: 新增分类对象
        :return: None
        """
        db_category = TopicCategory(
            parent_id=category.parent_id,
            category_name=category.category_name,
            description=category.description,
            order_num=category.order_num,
            create_by=category.create_by,
            create_time=category.create_time,
            update_by=category.update_by,
            update_time=category.update_time,
        )
        db.add(db_category)
        await db.flush()

    @classmethod
    async def update_category(cls, db: AsyncSession, category: TopicCategoryModel) -> None:
        """
        更新分类信息

        :param db: orm对象
        :param category: 更新分类对象
        :return: None
        """
        update_data = {}
        if category.parent_id is not None:
            update_data['parent_id'] = category.parent_id
        if category.category_name:
            update_data['category_name'] = category.category_name
        if category.description:
            update_data['description'] = category.description
        if category.order_num is not None:
            update_data['order_num'] = category.order_num
        if category.update_by:
            update_data['update_by'] = category.update_by
        if category.update_time:
            update_data['update_time'] = category.update_time

        await db.execute(
            update(TopicCategory)
            .where(TopicCategory.category_id == category.category_id)
            .values(**update_data)
        )

    @classmethod
    async def delete_category(cls, db: AsyncSession, category_ids: List[int], update_by: str, update_time: datetime) -> None:
        """
        删除分类信息

        :param db: orm对象
        :param category_ids: 需要删除的分类ID列表
        :param update_by: 更新者
        :param update_time: 更新时间
        :return: None
        """
        await db.execute(
            update(TopicCategory)
            .where(TopicCategory.category_id.in_(category_ids))
            .values(del_flag='2', update_by=update_by, update_time=update_time)
        )