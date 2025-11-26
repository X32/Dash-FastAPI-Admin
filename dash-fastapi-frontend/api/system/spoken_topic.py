from utils.request import api_request
from config.enums import ApiMethod
from config.env import ApiConfig


def get_spoken_topic_list(params):
    """
    获取话题列表
    :param params: 查询参数
    :return: 话题列表
    """
    return api_request("/api/v1/spokenTopic/list", method=ApiMethod.GET, params=params)


def add_spoken_topic(data):
    """
    新增话题
    :param data: 话题数据
    :return: 新增结果
    """
    return api_request("/api/v1/spokenTopic", method=ApiMethod.POST, json=data)


def edit_spoken_topic(data):
    """
    编辑话题
    :param data: 话题数据
    :return: 编辑结果
    """
    return api_request("/api/v1/spokenTopic", method=ApiMethod.PUT, json=data)


def delete_spoken_topic(topic_ids):
    """
    删除话题
    :param topic_ids: 话题ID列表
    :return: 删除结果
    """
    return api_request(f"/api/v1/spokenTopic/{topic_ids}", method=ApiMethod.DELETE)


def get_spoken_topic_detail(topic_id):
    """
    获取话题详情
    :param topic_id: 话题ID
    :return: 话题详情
    """
    return api_request(f"/api/v1/spokenTopic/{topic_id}", method=ApiMethod.GET)
