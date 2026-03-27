from typing import List, Optional
from sqlalchemy.orm import Session
from ..dao.topic_category_dao import TopicCategoryDao
from ..entity.topic_category_do import TopicCategoryDO
from exceptions.exception import ServiceException

class TopicCategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.topic_category_dao = TopicCategoryDao(db)

    def get_by_id(self, id: int) -> Optional[TopicCategoryDO]:
        """根据ID获取分类"""
        return self.topic_category_dao.get_by_id(id)

    def get_first_level_categories(self) -> List[TopicCategoryDO]:
        """获取所有一级分类"""
        return self.topic_category_dao.get_first_level_categories()

    def get_second_level_categories(self, parent_id: int) -> List[TopicCategoryDO]:
        """获取指定一级分类下的所有二级分类"""
        # 检查父分类是否存在且为一级分类
        parent_category = self.topic_category_dao.get_by_id(parent_id)
        if not parent_category:
            raise ServiceException(f"父分类ID {parent_id} 不存在")
        if parent_category.parent_id != 0:
            raise ServiceException(f"分类ID {parent_id} 不是一级分类")

        return self.topic_category_dao.get_second_level_categories(parent_id)

    def create_category(self, category_name: str, category_desc: str = '', parent_id: int = 0, sort_order: int = 0) -> TopicCategoryDO:
        """创建分类"""
        # 检查分类名称是否已存在于同层级
        existing_category = self.topic_category_dao.get_by_name_and_parent_id(category_name, parent_id)
        if existing_category:
            raise ServiceException(f"同层级已存在名称为 {category_name} 的分类")

        # 检查父分类是否存在（如果parent_id不为0）
        if parent_id != 0:
            parent_category = self.topic_category_dao.get_by_id(parent_id)
            if not parent_category:
                raise ServiceException(f"父分类ID {parent_id} 不存在")
            if parent_category.parent_id != 0:
                raise ServiceException(f"分类ID {parent_id} 不是一级分类，不支持三级分类")

        # 创建分类
        category = TopicCategoryDO(
            category_name=category_name,
            category_desc=category_desc,
            parent_id=parent_id,
            sort_order=sort_order
        )

        return self.topic_category_dao.create(category)

    def update_category(self, id: int, category_name: str = None, category_desc: str = None, parent_id: int = None, sort_order: int = None) -> TopicCategoryDO:
        """更新分类"""
        # 检查分类是否存在
        category = self.topic_category_dao.get_by_id(id)
        if not category:
            raise BusinessException(f"分类ID {id} 不存在")

        # 如果修改了分类名称，检查是否已存在于同层级
        if category_name and category_name != category.category_name:
            existing_category = self.topic_category_dao.get_by_name_and_parent_id(category_name, parent_id if parent_id is not None else category.parent_id)
            if existing_category:
                raise BusinessException(f"同层级已存在名称为 {category_name} 的分类")

        # 如果修改了父分类ID，检查父分类是否存在且为一级分类
        if parent_id is not None and parent_id != category.parent_id:
            if parent_id != 0:
                parent_category = self.topic_category_dao.get_by_id(parent_id)
                if not parent_category:
                    raise BusinessException(f"父分类ID {parent_id} 不存在")
                if parent_category.parent_id != 0:
                    raise BusinessException(f"分类ID {parent_id} 不是一级分类，不支持三级分类")

        # 更新分类信息
        if category_name is not None:
            category.category_name = category_name
        if category_desc is not None:
            category.category_desc = category_desc
        if parent_id is not None:
            category.parent_id = parent_id
        if sort_order is not None:
            category.sort_order = sort_order

        return self.topic_category_dao.update(category)

    def delete_category(self, id: int) -> bool:
        """删除分类"""
        # 检查分类是否存在
        category = self.topic_category_dao.get_by_id(id)
        if not category:
            raise BusinessException(f"分类ID {id} 不存在")

        # 检查分类是否有子分类
        if self.topic_category_dao.has_children(id):
            raise BusinessException(f"分类ID {id} 存在子分类，无法删除")

        # 这里可以添加检查分类是否关联话题的逻辑
        # 例如：if self.topic_service.has_topics_by_category(id):
        #         raise BusinessException(f"分类ID {id} 存在关联话题，无法删除")

        return self.topic_category_dao.delete(id)