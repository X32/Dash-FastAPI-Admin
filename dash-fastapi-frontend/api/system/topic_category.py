from config.enums import ApiMethod
from utils.request import api_request


class TopicCategoryApi:
    """
    话题分类管理模块相关接口
    """

    @classmethod
    def list_topic_category(cls, query: dict):
        """
        查询话题分类列表接口

        :param query: 查询话题分类参数
        :return:
        """
        return api_request(
            url='/admin/topicCategory/list',
            method=ApiMethod.GET,
            params=query,
        )

    @classmethod
    def get_topic_category(cls, category_id: int):
        """
        查询话题分类详情接口

        :param category_id: 分类id
        :return:
        """
        return api_request(
            url=f'/admin/topicCategory/{category_id}',
            method=ApiMethod.GET,
        )

    @classmethod
    def add_topic_category(cls, json: dict):
        """
        新增话题分类接口

        :param json: 新增话题分类参数
        :return:
        """
        return api_request(
            url='/admin/topicCategory',
            method=ApiMethod.POST,
            json=json,
        )

    @classmethod
    def update_topic_category(cls, json: dict):
        """
        修改话题分类接口

        :param json: 修改话题分类参数
        :return:
        """
        return api_request(
            url='/admin/topicCategory',
            method=ApiMethod.PUT,
            json=json,
        )

    @classmethod
    def del_topic_category(cls, category_id: str):
        """
        删除话题分类接口

        :param category_id: 分类id
        :return:
        """
        return api_request(
            url=f'/admin/topicCategory/{category_id}',
            method=ApiMethod.DELETE,
        )

    @classmethod
    def tree_select_topic_category(cls):
        """
        获取话题分类树形选择列表接口

        :return:
        """
        return api_request(
            url='/admin/topicCategory/treeSelect',
            method=ApiMethod.GET,
        )