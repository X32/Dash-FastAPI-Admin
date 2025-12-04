from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic_validation_decorator import NotBlank, Size
from typing import Optional, List


class TopicCategoryModel(BaseModel):
    """
    话题分类表对应pydantic模型
    """

    model_config = ConfigDict(from_attributes=True)

    category_id: Optional[int] = Field(default=None, description='分类ID')
    parent_id: Optional[int] = Field(default=None, description='父分类ID')
    category_name: Optional[str] = Field(default=None, description='分类名称')
    description: Optional[str] = Field(default=None, description='分类描述')
    order_num: Optional[int] = Field(default=None, description='显示顺序')
    del_flag: Optional[str] = Field(default=None, description='删除标志（0代表存在 2代表删除）')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    children: Optional[List['TopicCategoryModel']] = Field(default=None, description='子分类列表')

    @NotBlank(field_name='category_name', message='分类名称不能为空')
    @Size(field_name='category_name', min_length=0, max_length=50, message='分类名称长度不能超过50个字符')
    def get_category_name(self):
        return self.category_name

    @Size(field_name='description', min_length=0, max_length=200, message='分类描述长度不能超过200个字符')
    def get_description(self):
        return self.description

    @NotBlank(field_name='order_num', message='显示顺序不能为空')
    def get_order_num(self):
        return self.order_num

    def validate_fields(self):
        self.get_category_name()
        self.get_description()
        self.get_order_num()


class TopicCategoryQueryModel(TopicCategoryModel):
    """
    话题分类不分页查询模型
    """

    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class DeleteTopicCategoryModel(BaseModel):
    """
    删除话题分类模型
    """

    category_ids: str = Field(default=None, description='需要删除的分类ID')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[str] = Field(default=None, description='更新时间')