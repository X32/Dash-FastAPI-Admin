import feffery_antd_components as fac
from dash import dcc, html
from components.ApiRadioGroup import ApiRadioGroup
from components.ApiSelect import ApiSelect
from utils.permission_util import PermissionManager


# Initialize permission manager
permission_manager = PermissionManager()


def render(*args, **kwargs):
    return [
        # 话题管理模块操作类型存储容器
        dcc.Store(id='spoken-topic-operations-store'),
        # 话题管理模块弹窗类型存储容器
        dcc.Store(id='spoken-topic-modal_type-store'),
        # 话题管理模块表单数据存储容器
        dcc.Store(id='spoken-topic-form-store'),
        # 话题管理模块删除操作行key存储容器
        dcc.Store(id='spoken-topic-delete-ids-store'),
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
                                                                    id='spoken-topic-topic_name-input',
                                                                    placeholder='请输入话题名称',
                                                                    autoComplete='off',
                                                                    allowClear=True,
                                                                    style={
                                                                        'width': 240
                                                                    },
                                                                ),
                                                                label='话题名称',
                                                            ),
                                                            fac.AntdFormItem(
                                                                ApiSelect(
                                                                    id='spoken-topic-category_id-select',
                                                                    placeholder='请选择分类',
                                                                    style={
                                                                        'width': 240
                                                                    },
                                                                ),
                                                                label='分类',
                                                            ),
                                                            fac.AntdFormItem(
                                                                ApiRadioGroup(
                                                                    dict_type='sys_normal_disable',
                                                                    id='spoken-topic-status-radio',
                                                                    style={
                                                                        'width': 240
                                                                    }
                                                                ),
                                                                label='话题状态',
                                                            ),
                                                            fac.AntdFormItem(
                                                                fac.AntdButton(
                                                                    '搜索',
                                                                    id='spoken-topic-search',
                                                                    type='primary',
                                                                    icon=fac.AntdIcon(
                                                                        icon='antd-search'
                                                                    ),
                                                                )
                                                            ),
                                                            fac.AntdFormItem(
                                                                fac.AntdButton(
                                                                    '重置',
                                                                    id='spoken-topic-reset',
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
                                        id='spoken-topic-search-form-container',
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
                                                id='spoken-topic-add',
                                                type='primary',
                                                style={
                                                    'display': 'none'
                                                }
                                            ) if permission_manager.check_perms('system:spokenTopic:add') else None,
                                            fac.AntdButton(
                                                [
                                                    fac.AntdIcon(
                                                        icon='antd-delete'
                                                    ),
                                                    '删除'
                                                ],
                                                id='spoken-topic-delete',
                                                style={
                                                    'display': 'none'
                                                }
                                            ) if permission_manager.check_perms('system:spokenTopic:remove') else None,
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
                                        id='spoken-topic-table',
                                        columns=[
                                            {
                                                'title': '话题名称',
                                                'dataIndex': 'topic_name',
                                                'key': 'topic_name'
                                            },
                                            {
                                                'title': '分类名称',
                                                'dataIndex': 'category_name',
                                                'key': 'category_name'
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
                                                                'id': 'spoken-topic-edit',
                                                                'display': 'none'
                                                            } if permission_manager.check_perms('system:spokenTopic:edit') else None,
                                                            {
                                                                'content': '删除',
                                                                'icon': 'antd-delete',
                                                                'id': 'spoken-topic-delete-single',
                                                                'display': 'none'
                                                            } if permission_manager.check_perms('system:spokenTopic:remove') else None,
                                                        ]
                                                    }
                                                }
                                            }
                                        ],
                                        data=[],
                                        rowKey='topic_id',
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
        # 新增/编辑话题弹窗
        fac.AntdModal(
            id='spoken-topic-modal',
            title='话题管理',
            visible=False,
            width=500,
            okText='保存',
            cancelText='取消',
            maskClosable=False,
            children=[
                fac.AntdForm(
                    [
                        fac.AntdFormItem(
                            ApiSelect(
                                id='spoken-topic-category_id-select-modal',
                                placeholder='请选择分类',
                                style={
                                    'width': '100%'
                                }
                            ),
                            label='分类',
                            required=True
                        ),
                        fac.AntdFormItem(
                            fac.AntdInput(
                                id='spoken-topic-topic_name-input-modal',
                                placeholder='请输入话题名称',
                                autoComplete='off',
                                allowClear=True,
                                style={
                                    'width': '100%'
                                }
                            ),
                            label='话题名称',
                            required=True
                        ),
                        fac.AntdFormItem(
                            fac.AntdInputNumber(
                                id='spoken-topic-order_num-input-modal',
                                placeholder='请输入排序',
                                allowClear=True,
                                style={
                                    'width': '100%'
                                },
                                min=0
                            ),
                            label='排序'
                        ),
                        fac.AntdFormItem(
                            ApiRadioGroup(
                                dict_type='sys_normal_disable',
                                id='spoken-topic-status-radio-modal',
                                style={
                                    'width': '100%'
                                }
                            ),
                            label='状态'
                        )
                    ],
                    id='spoken-topic-form',
                    layout='vertical',
                )
            ]
        )
    ]


# Register callback
from callbacks.system_c import spoken_topic_c
