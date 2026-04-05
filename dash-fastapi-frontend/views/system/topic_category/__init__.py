import feffery_antd_components as fac
from dash import dcc, html
from callbacks.system_c import topic_category_c
from components.ApiRadioGroup import ApiRadioGroup
from components.ApiSelect import ApiSelect
from utils.permission_util import PermissionManager


def render(*args, **kwargs):
    query_params = {}
    table_data, default_expanded_row_keys = topic_category_c.generate_topic_category_table(
        query_params
    )

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
                                                    '新增',
                                                ],
                                                id={
                                                    'type': 'topic-category-operation-button',
                                                    'index': 'add',
                                                },
                                                style={
                                                    'color': '#1890ff',
                                                    'background': '#e8f4ff',
                                                    'border-color': '#a3d3ff',
                                                },
                                            )
                                            if PermissionManager.check_perms(
                                                'system:topicCategory:add'
                                            )
                                            else [],
                                            fac.AntdButton(
                                                [
                                                    fac.AntdIcon(
                                                        icon='antd-swap'
                                                    ),
                                                    '展开/折叠',
                                                ],
                                                id='topic-category-fold',
                                                style={
                                                    'color': '#909399',
                                                    'background': '#f4f4f5',
                                                    'border-color': '#d3d4d6',
                                                },
                                            ),
                                        ],
                                        style={'paddingBottom': '10px'},
                                    ),
                                    span=16,
                                ),
                                fac.AntdCol(
                                    fac.AntdSpace(
                                        [
                                            html.Div(
                                                fac.AntdTooltip(
                                                    fac.AntdButton(
                                                        [
                                                            fac.AntdIcon(
                                                                icon='antd-search'
                                                            ),
                                                        ],
                                                        id='topic-category-hidden',
                                                        shape='circle',
                                                    ),
                                                    id='topic-category-hidden-tooltip',
                                                    title='隐藏搜索',
                                                )
                                            ),
                                            html.Div(
                                                fac.AntdTooltip(
                                                    fac.AntdButton(
                                                        [
                                                            fac.AntdIcon(
                                                                icon='antd-sync'
                                                            ),
                                                        ],
                                                        id='topic-category-refresh',
                                                        shape='circle',
                                                    ),
                                                    title='刷新',
                                                )
                                            ),
                                        ],
                                        style={
                                            'float': 'right',
                                            'paddingBottom': '10px',
                                        },
                                    ),
                                    span=8,
                                    style={'paddingRight': '10px'},
                                ),
                            ],
                            gutter=5,
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdSpin(
                                        fac.AntdTable(
                                            id='topic-category-list-table',
                                            data=table_data,
                                            columns=[
                                                {
                                                    'dataIndex': 'category_id',
                                                    'title': '分类编号',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                    'hidden': True,
                                                },
                                                {
                                                    'dataIndex': 'category_name',
                                                    'title': '分类名称',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'category_description',
                                                    'title': '分类描述',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'order_num',
                                                    'title': '排序',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'status',
                                                    'title': '状态',
                                                    'renderOptions': {
                                                        'renderType': 'tags',
                                                        'renderTags': {
                                                            '0': {'color': 'blue', 'tag': '正常'},
                                                            '1': {'color': 'red', 'tag': '停用'}
                                                        }
                                                    },
                                                },
                                                {
                                                    'dataIndex': 'create_time',
                                                    'title': '创建时间',
                                                    'renderOptions': {
                                                        'renderType': 'ellipsis'
                                                    },
                                                },
                                                {
                                                    'title': '操作',
                                                    'dataIndex': 'operation',
                                                    'width': '15%',
                                                    'renderOptions': {
                                                        'renderType': 'button',
                                                        'renderButton': [
                                                            {
                                                                'title': '修改',
                                                                'icon': 'antd-edit',
                                                                'type': 'link',
                                                                'custom': 'edit',
                                                                'id': {
                                                                    'type': 'topic-category-operation-button',
                                                                    'index': 'edit',
                                                                },
                                                                'style': {
                                                                    'color': '#1890ff'
                                                                }
                                                            },
                                                            {
                                                                'title': '新增',
                                                                'icon': 'antd-plus',
                                                                'type': 'link',
                                                                'custom': 'add',
                                                                'id': {
                                                                    'type': 'topic-category-operation-button',
                                                                    'index': 'add_child',
                                                                },
                                                                'style': {
                                                                    'color': '#52c41a'
                                                                }
                                                            },
                                                            {
                                                                'title': '删除',
                                                                'icon': 'antd-delete',
                                                                'type': 'link',
                                                                'custom': 'delete',
                                                                'id': {
                                                                    'type': 'topic-category-operation-button',
                                                                    'index': 'delete',
                                                                },
                                                                'style': {
                                                                    'color': '#ff4d4f'
                                                                }
                                                            },
                                                        ],
                                                        'condition': [
                                                            PermissionManager.check_perms(
                                                                'system:topicCategory:edit'
                                                            ),
                                                            PermissionManager.check_perms(
                                                                'system:topicCategory:add'
                                                            ),
                                                            PermissionManager.check_perms(
                                                                'system:topicCategory:remove'
                                                            ),
                                                        ]
                                                    },
                                                },
                                            ],
                                            bordered=True,
                                            size='small',
                                            tableLayout='auto',
                                            pagination={
                                                'hideOnSinglePage': True
                                            },
                                            defaultExpandedRowKeys=default_expanded_row_keys,
                                            style={
                                                'width': '100%',
                                                'padding-right': '10px',
                                                'padding-bottom': '20px',
                                            },
                                        ),
                                        text='数据加载中',
                                    ),
                                )
                            ]
                        ),
                    ],
                    span=24,
                )
            ],
            gutter=5,
        ),
        # 新增和编辑话题分类表单modal
        fac.AntdModal(
            [
                fac.AntdForm(
                    [
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    html.Div(
                                        [
                                            fac.AntdFormItem(
                                                fac.AntdTreeSelect(
                                                    id='topic-category-tree-select',
                                                    name='parent_id',
                                                    placeholder='请选择上级分类',
                                                    treeData=[],
                                                    treeNodeFilterProp='title',
                                                    style={'width': '100%'},
                                                ),
                                                label='上级分类',
                                                required=True,
                                                id={
                                                    'type': 'topic-category-form-label',
                                                    'index': 'parent_id',
                                                    'required': True,
                                                },
                                                labelCol={'span': 4},
                                                wrapperCol={'span': 20},
                                            ),
                                        ],
                                        id='topic-category-parent_id-div',
                                        hidden=False,
                                    ),
                                    span=24,
                                ),
                            ]
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdInput(
                                            name='category_name',
                                            placeholder='请输入分类名称',
                                            allowClear=True,
                                            style={'width': '100%'},
                                        ),
                                        label='分类名称',
                                        required=True,
                                        id={
                                            'type': 'topic-category-form-label',
                                            'index': 'category_name',
                                            'required': True,
                                        },
                                    ),
                                    span=12,
                                ),
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdInputNumber(
                                            name='order_num',
                                            min=0,
                                            style={'width': '100%'},
                                        ),
                                        label='显示顺序',
                                        required=True,
                                        id={
                                            'type': 'topic-category-form-label',
                                            'index': 'order_num',
                                            'required': True,
                                        },
                                    ),
                                    span=12,
                                ),
                            ],
                            gutter=5,
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        fac.AntdInput(
                                            name='category_description',
                                            placeholder='请输入分类描述',
                                            allowClear=True,
                                            style={'width': '100%'},
                                        ),
                                        label='分类描述',
                                        id={
                                            'type': 'topic-category-form-label',
                                            'index': 'category_description',
                                            'required': False,
                                        },
                                    ),
                                    span=24,
                                ),
                            ]
                        ),
                        fac.AntdRow(
                            [
                                fac.AntdCol(
                                    fac.AntdFormItem(
                                        ApiRadioGroup(
                                            dict_type='sys_normal_disable',
                                            name='status',
                                            defaultValue='0',
                                            style={'width': '100%'},
                                        ),
                                        label='分类状态',
                                        id={
                                            'type': 'topic-category-form-label',
                                            'index': 'status',
                                            'required': False,
                                        },
                                    ),
                                    span=12,
                                ),
                            ],
                            gutter=5,
                        ),
                    ],
                    id='topic-category-form',
                    enableBatchControl=True,
                    labelCol={'span': 8},
                    wrapperCol={'span': 16},
                    style={'marginRight': '15px'},
                )
            ],
            id='topic-category-modal',
            mask=False,
            width=650,
            renderFooter=True,
            okClickClose=False,
        ),
        # 删除话题分类二次确认modal
        fac.AntdModal(
            fac.AntdText('是否确认删除？', id='topic-category-delete-text'),
            id='topic-category-delete-confirm-modal',
            visible=False,
            title='提示',
            renderFooter=True,
            centered=True,
        ),
    ]