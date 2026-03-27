from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions.exception import BusinessException
from spoken_classification.entity.topic_classification import (
    TopicClassificationEntity,
    TopicClassificationCreateRequest,
    TopicClassificationUpdateRequest,
    TopicClassificationQueryRequest
)
from spoken_classification.dao.topic_classification_dao import TopicClassificationDao


class TopicClassificationService:
    """话题分类Service层"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = TopicClassificationDao(db)

    async def get_classification_by_id(self, id: int) -> Optional[TopicClassificationEntity]:
        """根据ID获取分类信息"""
        return await self.dao.get_by_id(id)

    async def create_classification(self, request: TopicClassificationCreateRequest) -> TopicClassificationEntity:
        """创建分类"""
        # 校验同层级名称唯一
        existing = await self.dao.get_by_name_and_parent_id(request.name, request.parent_id)
        if existing:
            raise BusinessException(f"同一层级下已存在名称为'{request.name}'的分类")

        # 转换为Entity
        classification = TopicClassificationEntity(
            name=request.name,
            description=request.description,
            parent_id=request.parent_id,
            sort_order=request.sort_order
        )

        # 创建分类
        return await self.dao.create(classification)

    async def update_classification(self, request: TopicClassificationUpdateRequest) -> TopicClassificationEntity:
        """更新分类"""
        # 校验分类是否存在
        classification = await self.dao.get_by_id(request.id)
        if not classification:
            raise BusinessException("分类不存在")

        # 校验同层级名称唯一（排除自身）
        existing = await self.dao.get_by_name_and_parent_id(request.name, request.parent_id)
        if existing and existing.id != request.id:
            raise BusinessException(f"同一层级下已存在名称为'{request.name}'的分类")

        # 更新分类信息
        classification.name = request.name
        classification.description = request.description
        classification.parent_id = request.parent_id
        classification.sort_order = request.sort_order

        # 保存更新
        return await self.dao.update(classification)

    async def delete_classification(self, id: int) -> bool:
        """删除分类"""
        # 校验分类是否存在
        classification = await self.dao.get_by_id(id)
        if not classification:
            raise BusinessException("分类不存在")

        # 校验是否有子分类
        if await self.dao.check_has_children(id):
            raise BusinessException("该分类下存在子分类，无法删除")

        # 校验是否有关联话题
        if await self.dao.check_has_topics(id):
            raise BusinessException("该分类下存在关联话题，无法删除")

        # 软删除分类
        return await self.dao.delete(id)

    async def batch_delete_classification(self, ids: List[int]) -> Tuple[int, List[int]]:
        """批量删除分类"""
        failed_ids = []
        for id in ids:
            try:
                await self.delete_classification(id)
            except BusinessException:
                failed_ids.append(id)
        return len(ids) - len(failed_ids), failed_ids

    async def get_first_level_classifications(self, page: int, page_size: int) -> Tuple[List[TopicClassificationEntity], int]:
        """获取一级分类列表（分页）"""
        classifications = await self.dao.get_all_first_level(page, page_size)
        total = await self.dao.get_total_first_level()
        return classifications, total

    async def get_second_level_classifications(self, parent_id: int, page: int, page_size: int) -> Tuple[List[TopicClassificationEntity], int]:
        """获取指定一级分类下的二级分类列表（分页）"""
        # 校验父分类是否存在且为一级分类
        parent = await self.dao.get_by_id(parent_id)
        if not parent:
            raise BusinessException("父分类不存在")
        if parent.parent_id != 0:
            raise BusinessException("只能获取一级分类下的二级分类")

        classifications = await self.dao.get_list_by_parent_id(parent_id, page, page_size)
        total = await self.dao.get_total_by_parent_id(parent_id)
        return classifications, total

    async def get_classifications_by_parent_id(self, parent_id: int, page: int, page_size: int) -> Tuple[List[TopicClassificationEntity], int]:
        """根据父ID获取分类列表（分页）"""
        classifications = await self.dao.get_list_by_parent_id(parent_id, page, page_size)
        total = await self.dao.get_total_by_parent_id(parent_id)
        return classifications, total