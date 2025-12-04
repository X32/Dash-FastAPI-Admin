from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..entity.topic_category_do import TopicCategoryDO

class TopicCategoryDao:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[TopicCategoryDO]:
        """根据ID获取分类"""
        return self.db.query(TopicCategoryDO).filter(
            TopicCategoryDO.id == id,
            TopicCategoryDO.is_deleted == False
        ).first()

    def get_by_name_and_parent_id(self, category_name: str, parent_id: int) -> Optional[TopicCategoryDO]:
        """根据分类名称和父分类ID获取分类"""
        return self.db.query(TopicCategoryDO).filter(
            TopicCategoryDO.category_name == category_name,
            TopicCategoryDO.parent_id == parent_id,
            TopicCategoryDO.is_deleted == False
        ).first()

    def get_first_level_categories(self) -> List[TopicCategoryDO]:
        """获取所有一级分类"""
        return self.db.query(TopicCategoryDO).filter(
            TopicCategoryDO.parent_id == 0,
            TopicCategoryDO.is_deleted == False
        ).order_by(TopicCategoryDO.sort_order).all()

    def get_second_level_categories(self, parent_id: int) -> List[TopicCategoryDO]:
        """获取指定一级分类下的所有二级分类"""
        return self.db.query(TopicCategoryDO).filter(
            TopicCategoryDO.parent_id == parent_id,
            TopicCategoryDO.is_deleted == False
        ).order_by(TopicCategoryDO.sort_order).all()

    def get_all_categories(self) -> List[TopicCategoryDO]:
        """获取所有分类（包括一级和二级）"""
        return self.db.query(TopicCategoryDO).filter(
            TopicCategoryDO.is_deleted == False
        ).order_by(TopicCategoryDO.parent_id, TopicCategoryDO.sort_order).all()

    def create(self, category: TopicCategoryDO) -> TopicCategoryDO:
        """创建分类"""
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update(self, category: TopicCategoryDO) -> TopicCategoryDO:
        """更新分类"""
        self.db.merge(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, id: int) -> bool:
        """删除分类（软删除）"""
        category = self.get_by_id(id)
        if not category:
            return False

        category.is_deleted = True
        self.db.commit()
        return True

    def has_children(self, id: int) -> bool:
        """检查分类是否有子分类"""
        count = self.db.query(TopicCategoryDO).filter(
            TopicCategoryDO.parent_id == id,
            TopicCategoryDO.is_deleted == False
        ).count()
        return count > 0