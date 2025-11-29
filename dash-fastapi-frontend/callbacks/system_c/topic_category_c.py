import time
import uuid
from dash import ctx, dcc, no_update
from dash.dependencies import ALL, Input, Output, State
from dash.exceptions import PreventUpdate
from typing import Dict
from api.system.topic_category import *
from config.constant import SysYesNoConstant
from server import app
from utils.common_util import ValidateUtil
from utils.dict_util import DictManager
from utils.feedback_util import MessageManager
from utils.permission_util import PermissionManager
from utils.time_format_util import TimeFormatUtil


def generate_topic_category_table(query_params: Dict):
    """
    根据查询参数获取话题分类表格数据及分页信息

    :param query_params: 查询参数
    :return: 话题分类表格数据及分页信息
    """
    table_info = get_topic_category_list(query_params)
    table_data = table_info['rows']
    table_pagination = dict(
        pageSize=table_info['page_size'],
        current=table_info['page_num'],
        showSizeChanger=True,
        pageSizeOptions=[10, 30, 50, 100],
        showQuickJumper=True,
        total=table_info['total'],
    )
    for item in table_data:
        item['status'] = DictManager.get_dict_tag(
            dict_type='sys_normal_disable', dict_value=item.get('status')
        )
        item['create_time'] = TimeFormatUtil.format_time(
            item.get('create_time')
        )
        item['key'] = str(item['category_id'])
        item['operation'] = [
            {'content': '修改', 'type': 'link', 'icon': 'antd-edit'}
            if PermissionManager.check_perms('system:topicCategory:edit')
            else {},
            {'content': '删除', 'type': 'link', 'icon': 'antd-delete'}
            if PermissionManager.check_perms('system:topicCategory:remove')
            else {},
        ]

    return [table_data, table_pagination]


@app.callback(
    output=dict(
        topic_category_table_data=Output(
            'topic-category-list-table', 'data', allow_duplicate=True
        ),
        topic_category_table_pagination=Output(
            'topic-category-list-table', 'pagination', allow_duplicate=True
        ),
        topic_category_table_key=Output('topic-category-list-table', 'key', allow_duplicate=True),
        topic_category_table_selectedrowkeys=Output(
            'topic-category-list-table', 'selectedRowKeys', allow_duplicate=True
        ),
    ),
    inputs=dict(
        search_click=Input('topic-category-search', 'nClicks'),
        refresh_click=Input('topic-category-refresh', 'nClicks'),
        pagination=Input('topic-category-list-table', 'pagination'),
        operations=Input('topic-category-operations-store', 'data'),
    ),
    state=dict(
        category_name=State('topic-category-category_name-input', 'value'),
        status=State('topic-category-status-select', 'value'),
        create_time_range=State('topic-category-create_time-range', 'value'),
    ),
    prevent_initial_call=True,
)
def get_topic_category_table_data(
    search_click,
    refresh_click,
    pagination,
    operations,
    category_name,
    status,
    create_time_range,
):
    """
    获取话题分类表格数据回调（进行表格相关增删查改操作后均会触发此回调）
    """
    begin_time = None
    end_time = None
    if create_time_range:
        begin_time = create_time_range[0]
        end_time = create_time_range[1]

    query_params = dict(
        category_name=category_name,
        status=status,
        begin_time=begin_time,
        end_time=end_time,
        page_size=pagination['pageSize'] if pagination else 10,
        page_num=pagination['current'] if pagination else 1,
    )

    table_info = generate_topic_category_table(query_params)

    return dict(
        topic_category_table_data=table_info[0],
        topic_category_table_pagination=table_info[1],
        topic_category_table_key=str(uuid.uuid4()),
        topic_category_table_selectedrowkeys=[],
    )


@app.callback(
    output=dict(
        topic_category_modal_type=Output(
            'topic-category-modal_type-store', 'data'
        ),
        topic_category_form_data=Output('topic-category-form-store', 'data'),
        topic_category_modal_visible=Output('topic-category-modal', 'visible'),
    ),
    inputs=dict(
        add_click=Input('topic-category-add', 'nClicks'),
        edit_click=Input({'type': 'topic-category-edit-operation', 'index': ALL}, 'nClicks'),
    ),
    state=dict(
        table_selected_rows=State('topic-category-list-table', 'selectedRows'),
    ),
    prevent_initial_call=True,
)
def open_topic_category_modal(add_click, edit_click, table_selected_rows):
    """
    打开新增/编辑话题分类弹窗回调
    """
    ctx.triggered_id = ctx.triggered_id if ctx.triggered_id is not None else {}
    if ctx.triggered_id == 'topic-category-add':
        return dict(
            topic_category_modal_type='add',
            topic_category_form_data=dict(
                status='0',
            ),
            topic_category_modal_visible=True,
        )
    elif isinstance(ctx.triggered_id, dict) and ctx.triggered_id.get('type') == 'topic-category-edit-operation':
        if not table_selected_rows:
            MessageManager.open_fail_message(content='请选择一行数据进行编辑')
            raise PreventUpdate
        edit_id = table_selected_rows[0]['category_id']
        edit_data = get_topic_category_detail(edit_id)
        return dict(
            topic_category_modal_type='edit',
            topic_category_form_data=edit_data,
            topic_category_modal_visible=True,
        )

    raise PreventUpdate


@app.callback(
    output=dict(
        topic_category_modal_visible=Output('topic-category-modal', 'visible', allow_duplicate=True),
        topic_category_table_key=Output('topic-category-list-table', 'key', allow_duplicate=True),
    ),
    inputs=dict(
        confirm_click=Input('topic-category-confirm', 'nClicks'),
        cancel_click=Input('topic-category-cancel', 'nClicks'),
    ),
    state=dict(
        modal_type=State('topic-category-modal_type-store', 'data'),
        form_data=State('topic-category-form-store', 'data'),
    ),
    prevent_initial_call=True,
)
def save_topic_category(confirm_click, cancel_click, modal_type, form_data):
    """
    保存话题分类回调（新增/编辑）
    """
    if ctx.triggered_id == 'topic-category-cancel':
        return dict(
            topic_category_modal_visible=False,
            topic_category_table_key=no_update,
        )
    elif ctx.triggered_id == 'topic-category-confirm':
        # 表单验证
        if not form_data.get('category_name'):
            MessageManager.open_fail_message(content='分类名称不能为空')
            raise PreventUpdate
        if not form_data.get('status'):
            MessageManager.open_fail_message(content='分类状态不能为空')
            raise PreventUpdate

        # 处理数据
        submit_data = {
            'category_name': form_data.get('category_name'),
            'status': form_data.get('status'),
        }
        if modal_type == 'edit':
            submit_data['category_id'] = form_data.get('category_id')

        try:
            if modal_type == 'add':
                add_topic_category(submit_data)
                MessageManager.open_success_message(content='新增成功')
            elif modal_type == 'edit':
                edit_topic_category(submit_data)
                MessageManager.open_success_message(content='编辑成功')

            return dict(
                topic_category_modal_visible=False,
                topic_category_table_key=str(uuid.uuid4()),
            )
        except Exception as e:
            MessageManager.open_fail_message(content=f'{modal_type}失败：{str(e)}')
            raise PreventUpdate

    raise PreventUpdate


@app.callback(
    output=dict(
        topic_category_delete_ids=Output('topic-category-delete-ids-store', 'data'),
        topic_category_delete_modal_visible=Output('topic-category-delete-modal', 'visible', allow_duplicate=True),
    ),
    inputs=dict(
        delete_click=Input('topic-category-delete', 'nClicks'),
        operation_delete_click=Input({'type': 'topic-category-delete-operation', 'index': ALL}, 'nClicks'),
    ),
    state=dict(
        table_selected_rowkeys=State('topic-category-list-table', 'selectedRowKeys'),
    ),
    prevent_initial_call=True,
)
def open_topic_category_delete_modal(delete_click, operation_delete_click, table_selected_rowkeys):
    """
    打开删除话题分类弹窗回调
    """
    ctx.triggered_id = ctx.triggered_id if ctx.triggered_id is not None else {}
    if ctx.triggered_id == 'topic-category-delete' or (isinstance(ctx.triggered_id, dict) and ctx.triggered_id.get('type') == 'topic-category-delete-operation'):
        if not table_selected_rowkeys:
            MessageManager.open_fail_message(content='请选择至少一行数据进行删除')
            raise PreventUpdate

        return dict(
            topic_category_delete_ids=table_selected_rowkeys,
            topic_category_delete_modal_visible=True,
        )

    raise PreventUpdate


@app.callback(
    output=dict(
        topic_category_delete_modal_visible=Output('topic-category-delete-modal', 'visible', allow_duplicate=True),
        topic_category_table_key=Output('topic-category-list-table', 'key', allow_duplicate=True),
    ),
    inputs=dict(
        delete_confirm_click=Input('topic-category-delete-confirm', 'nClicks'),
        delete_cancel_click=Input('topic-category-delete-cancel', 'nClicks'),
    ),
    state=dict(
        delete_ids=State('topic-category-delete-ids-store', 'data'),
    ),
    prevent_initial_call=True,
)
def confirm_topic_category_delete(delete_confirm_click, delete_cancel_click, delete_ids):
    """
    确认删除话题分类回调
    """
    if ctx.triggered_id == 'topic-category-delete-cancel':
        return dict(
            topic_category_delete_modal_visible=False,
            topic_category_table_key=no_update,
        )
    elif ctx.triggered_id == 'topic-category-delete-confirm':
        try:
            delete_topic_category(','.join(delete_ids))
            MessageManager.open_success_message(content='删除成功')
            return dict(
                topic_category_delete_modal_visible=False,
                topic_category_table_key=str(uuid.uuid4()),
            )
        except Exception as e:
            MessageManager.open_fail_message(content=f'删除失败：{str(e)}')
            raise PreventUpdate

    raise PreventUpdate
