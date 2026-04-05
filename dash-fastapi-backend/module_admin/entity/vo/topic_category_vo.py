from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic_validation_decorator import NotBlank, Size
from typing import Literal, Optional


class TopicCategoryModel(BaseModel):
    """
    话题分类表对应pydantic模型
    """

    model_config = ConfigDict(from_attributes=True)

    category_id: Optional[int] = Field(default=None, description='分类id')
    parent_id: Optional[int] = Field(default=None, description='父分类id')
    category_name: Optional[str] = Field(default=None, description='分类名称')
    category_desc: Optional[str] = Field(default=None, description='分类描述')
    order_num: Optional[int] = Field(default=None, description='显示顺序')
    status: Optional[Literal['0', '1']] = Field(default=None, description='分类状态（0正常 1停用）')
    del_flag: Optional[Literal['0', '2']] = Field(default=None, description='删除标志（0代表存在 2代表删除）')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')

    @NotBlank(field_name='category_name', message='分类名称不能为空')
    @Size(field_name='category_name', min_length=0, max_length=50, message='分类名称长度不能超过50个字符')
    def get_category_name(self):
        return self.category_name

    @Size(field_name='category_desc', min_length=0, max_length=500, message='分类描述长度不能超过500个字符')
    def get_category_desc(self):
        return self.category_desc

    @NotBlank(field_name='order_num', message='显示顺序不能为空')
    def get_order_num(self):
        return self.order_num

    def validate_fields(self):
        self.get_category_name()
        self.get_category_desc()
        self.get_order_num()


class TopicCategoryQueryModel(TopicCategoryModel):
    """
    话题分类管理不分页查询模型
    """

    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class TopicCategoryPageQueryModel(TopicCategoryQueryModel):
    """
    话题分类管理分页查询模型
    """

    page_num: Optional[int] = Field(default=1, ge=1, description='当前页码')
    page_size: Optional[int] = Field(default=10, ge=1, le=1000, description='每页记录数')


class DeleteTopicCategoryModel(BaseModel):
    """
    删除话题分类模型
    """

    category_ids: str = Field(default=None, description='需要删除的分类id')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[str] = Field(default=None, description='更新时间')