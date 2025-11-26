from utils.request import api_request
from config.enums import ApiMethod
from config.env import ApiConfig


def get_topic_category_list(params):
    """
    获取话题分类列表
    :param params: 查询参数
    :return: 话题分类列表
    """
    return api_request("/api/v1/topicCategory/list", method=ApiMethod.GET, params=params)


def get_topic_category_tree():
    """
    获取话题分类树
    :return: 话题分类树
    """
    return api_request("/api/v1/topicCategory/tree", method=ApiMethod.GET)


def add_topic_category(data):
    """
    新增话题分类
    :param data: 话题分类数据
    :return: 新增结果
    """
    return api_request("/api/v1/topicCategory", method=ApiMethod.POST, json=data)


def edit_topic_category(category_id, data):
    """
    编辑话题分类
    :param category_id: 话题分类ID
    :param data: 话题分类数据
    :return: 编辑结果
    """
    return api_request(f"/api/v1/topicCategory/{category_id}", method=ApiMethod.PUT, json=data)


def delete_topic_category(category_id):
    """
    删除话题分类
    :param category_id: 话题分类ID
    :return: 删除结果
    """
    return api_request(f"/api/v1/topicCategory/{category_id}", method=ApiMethod.DELETE)


def get_topic_category_detail(category_id):
    """
    获取话题分类详情
    :param category_id: 话题分类ID
    :return: 话题分类详情
    """
    return api_request(f"/api/v1/topicCategory/{category_id}", method=ApiMethod.GET)
