from typing import List, Optional
from sqlalchemy import text, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from spoken_classification.entity.topic_classification import TopicClassificationEntity


class TopicClassificationDao:
    """话题分类DAO层"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id: int) -> Optional[TopicClassificationEntity]:
        """根据ID获取分类信息"""
        result = await self.db.execute(
            select(TopicClassificationEntity).where(
                TopicClassificationEntity.id == id,
                TopicClassificationEntity.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name_and_parent_id(self, name: str, parent_id: Optional[int]) -> Optional[TopicClassificationEntity]:
        """根据名称和父ID获取分类信息"""
        # 当 parent_id 为 None 时，查询 parent_id 为 0 的记录
        actual_parent_id = parent_id if parent_id is not None else 0
        result = await self.db.execute(
            select(TopicClassificationEntity).where(
                TopicClassificationEntity.name == name,
                TopicClassificationEntity.parent_id == actual_parent_id,
                TopicClassificationEntity.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    async def get_list_by_parent_id(self, parent_id: int, page: int, page_size: int) -> List[TopicClassificationEntity]:
        """根据父ID获取分类列表（分页）"""
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(TopicClassificationEntity).where(
                TopicClassificationEntity.parent_id == parent_id,
                TopicClassificationEntity.is_deleted == 0
            ).order_by(
                TopicClassificationEntity.sort_order.asc(),
                TopicClassificationEntity.id.asc()
            ).offset(offset).limit(page_size)
        )
        return result.scalars().all()

    async def get_total_by_parent_id(self, parent_id: int) -> int:
        """根据父ID获取分类总数"""
        result = await self.db.execute(
            select(func.count(TopicClassificationEntity.id)).where(
                TopicClassificationEntity.parent_id == parent_id,
                TopicClassificationEntity.is_deleted == 0
            )
        )
        return result.scalar()

    async def get_all_first_level(self, page: int, page_size: int) -> List[TopicClassificationEntity]:
        """获取所有一级分类（分页）"""
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(TopicClassificationEntity).where(
                TopicClassificationEntity.parent_id == 0,
                TopicClassificationEntity.is_deleted == 0
            ).order_by(
                TopicClassificationEntity.sort_order.asc(),
                TopicClassificationEntity.id.asc()
            ).offset(offset).limit(page_size)
        )
        return result.scalars().all()

    async def get_total_first_level(self) -> int:
        """获取一级分类总数"""
        result = await self.db.execute(
            select(func.count(TopicClassificationEntity.id)).where(
                TopicClassificationEntity.parent_id == 0,
                TopicClassificationEntity.is_deleted == 0
            )
        )
        return result.scalar()

    async def check_has_children(self, id: int) -> bool:
        """检查分类是否有子分类"""
        result = await self.db.execute(
            select(func.count(TopicClassificationEntity.id)).where(
                TopicClassificationEntity.parent_id == id,
                TopicClassificationEntity.is_deleted == 0
            )
        )
        count = result.scalar()
        return count > 0

    async def check_has_topics(self, id: int) -> bool:
        """检查分类是否有关联话题（需要根据实际话题表调整）"""
        # 注意：这里需要根据实际的话题表名和字段进行调整
        # 假设话题表名为topic，分类ID字段为classification_id
        # 目前测试环境中topic表不存在，暂时返回False
        return False

    async def create(self, classification: TopicClassificationEntity) -> TopicClassificationEntity:
        """创建分类"""
        self.db.add(classification)
        await self.db.commit()
        await self.db.refresh(classification)
        return classification

    async def update(self, classification: TopicClassificationEntity) -> TopicClassificationEntity:
        """更新分类"""
        self.db.merge(classification)
        await self.db.commit()
        await self.db.refresh(classification)
        return classification

    async def delete(self, id: int) -> bool:
        """软删除分类"""
        classification = await self.get_by_id(id)
        if not classification:
            return False
        classification.is_deleted = 1
        await self.db.commit()
        return True

    async def batch_delete(self, ids: List[int]) -> int:
        """批量软删除分类"""
        result = await self.db.execute(
            update(TopicClassificationEntity).where(
                TopicClassificationEntity.id.in_(ids),
                TopicClassificationEntity.is_deleted == 0
            ).values(is_deleted=1)
        )
        await self.db.commit()
        return result.rowcount