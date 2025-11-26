import feffery_antd_components as fac
from dash import dcc, html
from components.ApiRadioGroup import ApiRadioGroup
from components.ApiSelect import ApiSelect
from utils.permission_util import PermissionManager


# Initialize permission manager
permission_manager = PermissionManager()


def render(*args, **kwargs):
    return [
        # 话题分类管理模块操作类型存储容器
        dcc.Store(id='topic-category-operations-store'),
        # 话题分类管理模块弹窗类型存储容器
        dcc.Store(id='topic-category-modal_type-store'),
        # 话题分类管理模块表单数据存储容器
        dcc.Store(id='topic-category-form-store'),
        # 话题分类管理模块删除操作行key存储容器
        dcc.Store(id='topic-category-delete-ids-store'),
        fac.AntdRow(
            [
                fac.AntdCol(
                    [
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    html.Div(
                                        [
                                            fac.AntdForm(
                                                [
                                                    fac.AntdSpace(
                                                        [
                                                            fac.AntdFormItem(
                                                                fac.AntdInput(
                                                                    id='topic-category-category_name-input',
                                                                    placeholder='请输入分类名称',
                                                                    autoComplete='off',
                                                                    allowClear=True,
                                                                    style={
                                                                        'width': 240
                                                                    },
                                                                ),
                                                                label='分类名称',
                                                            ),
                                                            fac.AntdFormItem(
                                                                ApiSelect(
                                                                    dict_type='sys_normal_disable',
                                                                    id='topic-category-status-select',
                                                                    placeholder='分类状态',
                                                                    style={
                                                                        'width': 240
                                                                    },
                                                                ),
                                                                label='分类状态',
                                                            ),
                                                            fac.AntdFormItem(
                                                                fac.AntdButton(
                                                                    '搜索',
                                                                    id='topic-category-search',
                                                                    type='primary',
                                                                    icon=fac.AntdIcon(
                                                                        icon='antd-search'
                                                                    ),
                                                                )
                                                            ),
                                                            fac.AntdFormItem(
                                                                fac.AntdButton(
                                                                    '重置',
                                                                    id='topic-category-reset',
                                                                    icon=fac.AntdIcon(
                                                                        icon='antd-sync'
                                                                    ),
                                                                )
                                                            ),
                                                        ],
                                                        style={
                                                            'paddingBottom': '10px'
                                                        },
                                                    ),
                                                ],
                                                layout='inline',
                                            )
                                        ],
                                        hidden=False,
                                        id='topic-category-search-form-container',
                                    ),
                                )
                            ]
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdSpace(
                                        [
                                            fac.AntdButton(
                                                [
                                                    fac.AntdIcon(
                                                        icon='antd-plus'
                                                    ),
                                                    '新增'
                                                ],
                                                id='topic-category-add',
                                                type='primary',
                                                style={
                                                    'display': 'none'
                                                }
                                            ) if permission_manager.check_permission('system:topicCategory:add') else None,
                                            fac.AntdButton(
                                                [
                                                    fac.AntdIcon(
                                                        icon='antd-delete'
                                                    ),
                                                    '删除'
                                                ],
                                                id='topic-category-delete',
                                                style={
                                                    'display': 'none'
                                                }
                                            ) if permission_manager.check_permission('system:topicCategory:remove') else None,
                                        ],
                                        style={
                                            'paddingBottom': '10px'
                                        },
                                    )
                                )
                            ]
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdTable(
                                        id='topic-category-table',
                                        columns=[
                                            {
                                                'title': '分类名称',
                                                'dataIndex': 'category_name',
                                                'key': 'category_name'
                                            },
                                            {
                                                'title': '父分类',
                                                'dataIndex': 'parent_name',
                                                'key': 'parent_name'
                                            },
                                            {
                                                'title': '排序',
                                                'dataIndex': 'order_num',
                                                'key': 'order_num'
                                            },
                                            {
                                                'title': '状态',
                                                'dataIndex': 'status',
                                                'key': 'status',
                                                'renderOptions': {
                                                    'renderType': 'renderSwitch',
                                                    'props': {
                                                        'checkedChildren': '正常',
                                                        'unCheckedChildren': '停用'
                                                    }
                                                }
                                            },
                                            {
                                                'title': '创建时间',
                                                'dataIndex': 'create_time',
                                                'key': 'create_time'
                                            },
                                            {
                                                'title': '更新时间',
                                                'dataIndex': 'update_time',
                                                'key': 'update_time'
                                            },
                                            {
                                                'title': '操作',
                                                'dataIndex': 'action',
                                                'key': 'action',
                                                'fixed': 'right',
                                                'width': 150,
                                                'renderOptions': {
                                                    'renderType': 'renderButton',
                                                    'props': {
                                                        'buttons': [
                                                            {
                                                                'content': '编辑',
                                                                'icon': 'antd-edit',
                                                                'type': 'primary',
                                                                'id': 'topic-category-edit',
                                                                'display': 'none'
                                                            } if permission_manager.check_permission('system:topicCategory:edit') else None,
                                                            {
                                                                'content': '删除',
                                                                'icon': 'antd-delete',
                                                                'id': 'topic-category-delete-single',
                                                                'display': 'none'
                                                            } if permission_manager.check_permission('system:topicCategory:remove') else None,
                                                        ]
                                                    }
                                                }
                                            }
                                        ],
                                        data=[],
                                        rowKey='category_id',
                                        bordered=True,
                                        pagination={
                                            'pageSizeOptions': ['10', '20', '50', '100']
                                        },
                                        scroll={
                                            'x': 'max-content'
                                        },
                                        style={
                                            'width': '100%'
                                        },
                                    )
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        # 新增/编辑分类弹窗
        fac.AntdModal(
            id='topic-category-modal',
            title='分类管理',
            visible=False,
            width=500,
            okText='保存',
            cancelText='取消',
            maskClosable=False,
            children=[
                fac.AntdForm(
                    [
                        fac.AntdFormItem(
                            fac.AntdTreeSelect(
                                id='topic-category-parent_id-select',
                                placeholder='请选择父分类',
                                treeData=[],
                                treeDefaultExpandAll=True,
                                allowClear=True,
                                style={
                                    'width': '100%'
                                }
                            ),
                            label='父分类',
                            name='parent_id'
                        ),
                        fac.AntdFormItem(
                            fac.AntdInput(
                                id='topic-category-category_name-input-modal',
                                placeholder='请输入分类名称',
                                autoComplete='off',
                                allowClear=True,
                                style={
                                    'width': '100%'
                                }
                            ),
                            label='分类名称',
                            name='category_name',
                            required=True
                        ),
                        fac.AntdFormItem(
                            fac.AntdInputNumber(
                                id='topic-category-order_num-input-modal',
                                placeholder='请输入排序',
                                allowClear=True,
                                style={
                                    'width': '100%'
                                },
                                min=0
                            ),
                            label='排序',
                            name='order_num'
                        ),
                        fac.AntdFormItem(
                            ApiRadioGroup(
                                dict_type='sys_normal_disable',
                                id='topic-category-status-radio-modal',
                                style={
                                    'width': '100%'
                                }
                            ),
                            label='状态',
                            name='status'
                        )
                    ],
                    id='topic-category-form',
                    layout='vertical',
                )
            ]
        )
    ]


# Register callback
from callbacks.system_c import topic_category_c
