from pydantic import BaseModel, Field
from typing import Optional, TypeVar, Generic


T = TypeVar('T')


class CrudResponseModel(BaseModel):
    """
    CRUD操作统一返回模型
    """
    is_success: bool = Field(default=True, description='操作是否成功')
    message: str = Field(default='操作成功', description='返回消息')
    data: Optional[T] = Field(default=None, description='返回数据')


class PageResponseModel(BaseModel, Generic[T]):
    """
    分页查询统一返回模型
    """
    total: int = Field(default=0, description='总记录数')
    rows: Optional[list[T]] = Field(default=None, description='当前页数据')
    message: str = Field(default='查询成功', description='返回消息')


class ResponseModel(BaseModel, Generic[T]):
    """
    通用返回模型
    """
    code: int = Field(default=200, description='状态码')
    message: str = Field(default='操作成功', description='返回消息')
    data: Optional[T] = Field(default=None, description='返回数据')

    @classmethod
    def success(cls, data: Optional[T] = None, message: str = '操作成功') -> 'ResponseModel[T]':
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, message: str = '操作失败', code: int = 500) -> 'ResponseModel[T]':
        return cls(code=code, message=message, data=None)