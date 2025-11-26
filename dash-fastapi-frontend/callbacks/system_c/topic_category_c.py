import json
from datetime import datetime

from dash import Output, Input, State, html
from dash.exceptions import PreventUpdate

from api.system.topic_category import TopicCategoryApi
from config.constant import SysNormalDisableConstant
from utils.dict_util import DictManager
from utils.feedback_util import MessageManager
from utils.permission_util import PermissionManager
from utils.tree_util import TreeUtil


class TopicCategoryC:
    """
    话题分类管理回调
    """

    @classmethod
    def generate_topic_category_table(cls, data: dict):
        """
        根据话题分类数据生成表格数据

        :param data: 话题分类数据
        :return: 表格数据和列定义
        """
        if data is None:
            return [], []

        # 获取话题分类列表数据
        result = TopicCategoryApi.list_topic_category(data)
        if result.get('code') != 200:
            return [], []

        topic_category_data = result.get('data', {}).get('rows', [])
        
        # 转换为树形结构
        tree_data = TreeUtil.list_to_tree(topic_category_data)
        
        # 定义表格列
        columns = [
            {'title': '分类名称', 'dataIndex': 'category_name', 'width': '20%'},
            {'title': '分类编码', 'dataIndex': 'category_code', 'width': '15%'},
            {'title': '排序', 'dataIndex': 'order_num', 'width': '10%', 'sorter': True},
            {'title': '状态', 'dataIndex': 'status', 'width': '10%'},
            {'title': '创建时间', 'dataIndex': 'create_time', 'width': '15%'},
            {'title': '操作', 'dataIndex': 'operation', 'width': '20%'},
        ]

        # 处理表格数据
        table_data = []
        for item in tree_data:
            row_data = {
                'key': str(item.get('category_id')),
                'category_name': html.Div([
                    html.Span(item.get('category_name', '')),
                    html.Span(
                        f" ({item.get('category_code', '')})",
                        style={'color': '#999', 'fontSize': '12px'}
                    ) if item.get('category_code') else None
                ]),
                'category_code': item.get('category_code', ''),
                'order_num': item.get('order_num', 0),
                'status': DictManager.get_dict_label(
                    dict_type=SysNormalDisableConstant.DEFAULT,
                    dict_value=item.get('status', '0')
                ),
                'create_time': item.get('create_time', ''),
                'operation': html.Div([
                    PermissionManager.check_perms('system:topicCategory:edit') and html.A(
                        '修改',
                        id=f"edit-topicCategory-{item.get('category_id')}",
                        style={'marginRight': '8px', 'color': '#1890ff', 'cursor': 'pointer'}
                    ),
                    PermissionManager.check_perms('system:topicCategory:add') and html.A(
                        '新增',
                        id=f"add-topicCategory-{item.get('category_id')}",
                        style={'marginRight': '8px', 'color': '#52c41a', 'cursor': 'pointer'}
                    ),
                    PermissionManager.check_perms('system:topicCategory:remove') and html.A(
                        '删除',
                        id=f"delete-topicCategory-{item.get('category_id')}",
                        style={'color': '#ff4d4f', 'cursor': 'pointer'}
                    )
                ], style={'display': 'flex'})
            }
            table_data.append(row_data)

            # 添加子分类数据
            if 'children' in item and item['children']:
                cls._add_children_to_table(item['children'], table_data, columns)

        return table_data, columns

    @classmethod
    def _add_children_to_table(cls, children: list, table_data: list, columns: list, level: int = 1):
        """
        递归添加子分类到表格数据

        :param children: 子分类列表
        :param table_data: 表格数据列表
        :param columns: 表格列定义
        :param level: 层级深度
        """
        for child in children:
            indent = ' ' * (level * 2) + '└─ '
            row_data = {
                'key': str(child.get('category_id')),
                'category_name': html.Div([
                    html.Span(indent + child.get('category_name', '')),
                    html.Span(
                        f" ({child.get('category_code', '')})",
                        style={'color': '#999', 'fontSize': '12px'}
                    ) if child.get('category_code') else None
                ]),
                'category_code': child.get('category_code', ''),
                'order_num': child.get('order_num', 0),
                'status': DictManager.get_dict_label(
                    dict_type=SysNormalDisableConstant.DEFAULT,
                    dict_value=child.get('status', '0')
                ),
                'create_time': child.get('create_time', ''),
                'operation': html.Div([
                    PermissionManager.check_perms('system:topicCategory:edit') and html.A(
                        '修改',
                        id=f"edit-topicCategory-{child.get('category_id')}",
                        style={'marginRight': '8px', 'color': '#1890ff', 'cursor': 'pointer'}
                    ),
                    PermissionManager.check_perms('system:topicCategory:add') and html.A(
                        '新增',
                        id=f"add-topicCategory-{child.get('category_id')}",
                        style={'marginRight': '8px', 'color': '#52c41a', 'cursor': 'pointer'}
                    ),
                    PermissionManager.check_perms('system:topicCategory:remove') and html.A(
                        '删除',
                        id=f"delete-topicCategory-{child.get('category_id')}",
                        style={'color': '#ff4d4f', 'cursor': 'pointer'}
                    )
                ], style={'display': 'flex'})
            }
            table_data.append(row_data)

            # 递归处理子分类
            if 'children' in child and child['children']:
                cls._add_children_to_table(child['children'], table_data, columns, level + 1)

    @classmethod
    def get_topic_category_table_data(cls, search_value: dict, pagination: dict, **kwargs):
        """
        获取话题分类表格数据回调函数

        :param search_value: 搜索表单数据
        :param pagination: 分页配置
        :return: 更新表格数据和分页配置
        """
        if search_value is None:
            raise PreventUpdate

        # 构建查询参数
        query_params = {}
        if search_value:
            query_params.update(search_value)
        
        if pagination:
            query_params['page_num'] = pagination.get('current', 1)
            query_params['page_size'] = pagination.get('pageSize', 10)

        try:
            # 获取表格数据和列定义
            table_data, columns = cls.generate_topic_category_table(query_params)
            
            # 计算总数
            total = len(table_data)
            
            return [
                table_data,
                columns,
                {'current': query_params.get('page_num', 1), 'pageSize': query_params.get('page_size', 10), 'total': total},
                {'type': 'success', 'content': '数据加载成功'}
            ]
        except Exception as e:
            return [
                [],
                [],
                {'current': 1, 'pageSize': 10, 'total': 0},
                {'type': 'error', 'content': f'数据加载失败: {str(e)}'}
            ]

    @classmethod
    def refresh_topic_category_table_data(cls, search_click: int, refresh_click: int, search_value: dict, pagination: dict):
        """
        刷新话题分类表格数据

        :param search_click: 搜索按钮点击次数
        :param refresh_click: 刷新按钮点击次数
        :param search_value: 搜索表单数据
        :param pagination: 分页配置
        :return: 更新表格数据和分页配置
        """
        if not search_click and not refresh_click:
            raise PreventUpdate

        return cls.get_topic_category_table_data(search_value, pagination)

    @classmethod
    def reset_topic_category_search_form(cls, reset_click: int):
        """
        重置话题分类搜索表单

        :param reset_click: 重置按钮点击次数
        :return: 清空搜索表单数据
        """
        if not reset_click:
            raise PreventUpdate

        return {None: None}, {'current': 1, 'pageSize': 10}

    @classmethod
    def show_topic_category_search(cls, search_click: int, search_status: dict):
        """
        显示/隐藏话题分类搜索区域

        :param search_click: 搜索按钮点击次数
        :param search_status: 当前搜索区域状态
        :return: 更新搜索区域显示状态
        """
        if not search_click:
            raise PreventUpdate

        if search_status is None:
            search_status = {'display': 'block'}

        if search_status.get('display') == 'none':
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    @classmethod
    def get_topic_category_info(cls, category_id: int):
        """
        获取话题分类详情

        :param category_id: 分类ID
        :return: 分类详情数据
        """
        if category_id is None:
            return {}

        try:
            result = TopicCategoryApi.get_topic_category(category_id)
            if result.get('code') == 200:
                return result.get('data', {})
            else:
                MessageManager.error(f"获取分类详情失败: {result.get('msg', '未知错误')}")
                return {}
        except Exception as e:
            MessageManager.error(f"获取分类详情失败: {str(e)}")
            return {}

    @classmethod
    def add_topic_category_submit(cls, submit_click: int, form_value: dict, modal_type: str):
        """
        新增话题分类提交

        :param submit_click: 提交按钮点击次数
        :param form_value: 表单数据
        :param modal_type: 模态框类型
        :return: 提交结果
        """
        if not submit_click or modal_type != 'add':
            raise PreventUpdate

        if not form_value:
            MessageManager.warning('请填写完整的分类信息')
            return False, {'content': '请填写完整的分类信息', 'type': 'warning'}

        try:
            result = TopicCategoryApi.add_topic_category(form_value)
            if result.get('code') == 200:
                MessageManager.success('新增分类成功')
                return True, {'content': '新增分类成功', 'type': 'success'}
            else:
                error_msg = result.get('msg', '新增分类失败')
                MessageManager.error(error_msg)
                return False, {'content': error_msg, 'type': 'error'}
        except Exception as e:
            error_msg = f'新增分类失败: {str(e)}'
            MessageManager.error(error_msg)
            return False, {'content': error_msg, 'type': 'error'}

    @classmethod
    def update_topic_category_submit(cls, submit_click: int, form_value: dict, modal_type: str):
        """
        修改话题分类提交

        :param submit_click: 提交按钮点击次数
        :param form_value: 表单数据
        :param modal_type: 模态框类型
        :return: 提交结果
        """
        if not submit_click or modal_type != 'edit':
            raise PreventUpdate

        if not form_value:
            MessageManager.warning('请填写完整的分类信息')
            return False, {'content': '请填写完整的分类信息', 'type': 'warning'}

        try:
            result = TopicCategoryApi.update_topic_category(form_value)
            if result.get('code') == 200:
                MessageManager.success('修改分类成功')
                return True, {'content': '修改分类成功', 'type': 'success'}
            else:
                error_msg = result.get('msg', '修改分类失败')
                MessageManager.error(error_msg)
                return False, {'content': error_msg, 'type': 'error'}
        except Exception as e:
            error_msg = f'修改分类失败: {str(e)}'
            MessageManager.error(error_msg)
            return False, {'content': error_msg, 'type': 'error'}

    @classmethod
    def delete_topic_category_submit(cls, delete_click: int, category_id: int):
        """
        删除话题分类提交

        :param delete_click: 删除按钮点击次数
        :param category_id: 分类ID
        :return: 删除结果
        """
        if not delete_click or category_id is None:
            raise PreventUpdate

        try:
            result = TopicCategoryApi.del_topic_category(str(category_id))
            if result.get('code') == 200:
                MessageManager.success('删除分类成功')
                return True, {'content': '删除分类成功', 'type': 'success'}
            else:
                error_msg = result.get('msg', '删除分类失败')
                MessageManager.error(error_msg)
                return False, {'content': error_msg, 'type': 'error'}
        except Exception as e:
            error_msg = f'删除分类失败: {str(e)}'
            MessageManager.error(error_msg)
            return False, {'content': error_msg, 'type': 'error'}

    @classmethod
    def get_topic_category_tree_select_options(cls):
        """
        获取话题分类树形选择选项

        :return: 树形选择选项
        """
        try:
            result = TopicCategoryApi.tree_select_topic_category()
            if result.get('code') == 200:
                return result.get('data', [])
            else:
                return []
        except Exception as e:
            MessageManager.error(f'获取分类树形选项失败: {str(e)}')
            return []