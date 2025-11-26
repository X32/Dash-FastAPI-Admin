import time
import uuid
from dash import ctx, dcc, no_update
from dash.dependencies import ALL, Input, Output, State
from dash.exceptions import PreventUpdate
from typing import Dict
from api.system.spoken_topic import *
from config.constant import SysYesNoConstant
from server import app
from utils.common_util import ValidateUtil
from utils.dict_util import DictManager
from utils.feedback_util import MessageManager
from utils.permission_util import PermissionManager
from utils.time_format_util import TimeFormatUtil


def generate_spoken_topic_table(query_params: Dict):
    """
    根据查询参数获取话题表格数据及分页信息

    :param query_params: 查询参数
    :return: 话题表格数据及分页信息
    """
    table_info = get_spoken_topic_list(query_params)
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
        item['key'] = str(item['topic_id'])
        item['operation'] = [
            {'content': '修改', 'type': 'link', 'icon': 'antd-edit'}
            if PermissionManager.check_perms('system:spokenTopic:edit')
            else {},
            {'content': '删除', 'type': 'link', 'icon': 'antd-delete'}
            if PermissionManager.check_perms('system:spokenTopic:remove')
            else {},
        ]

    return [table_data, table_pagination]


@app.callback(
    output=dict(
        spoken_topic_table_data=Output(
            'spoken-topic-list-table', 'data', allow_duplicate=True
        ),
        spoken_topic_table_pagination=Output(
            'spoken-topic-list-table', 'pagination', allow_duplicate=True
        ),
        spoken_topic_table_key=Output('spoken-topic-list-table', 'key'),
        spoken_topic_table_selectedrowkeys=Output(
            'spoken-topic-list-table', 'selectedRowKeys'
        ),
    ),
    inputs=dict(
        search_click=Input('spoken-topic-search', 'nClicks'),
        refresh_click=Input('spoken-topic-refresh', 'nClicks'),
        pagination=Input('spoken-topic-list-table', 'pagination'),
        operations=Input('spoken-topic-operations-store', 'data'),
    ),
    state=dict(
        topic_name=State('spoken-topic-topic_name-input', 'value'),
        category_id=State('spoken-topic-category_id-select', 'value'),
        status=State('spoken-topic-status-radio', 'value'),
        create_time_range=State('spoken-topic-create_time-range', 'value'),
    ),
    prevent_initial_call=True,
)
def get_spoken_topic_table_data(
    search_click,
    refresh_click,
    pagination,
    operations,
    topic_name,
    category_id,
    status,
    create_time_range,
):
    """
    获取话题表格数据回调（进行表格相关增删查改操作后均会触发此回调）
    """
    begin_time = None
    end_time = None
    if create_time_range:
        begin_time = create_time_range[0]
        end_time = create_time_range[1]

    query_params = dict(
        topic_name=topic_name,
        category_id=category_id,
        status=status,
        begin_time=begin_time,
        end_time=end_time,
        page_size=pagination['pageSize'] if pagination else 10,
        page_num=pagination['current'] if pagination else 1,
    )

    table_info = generate_spoken_topic_table(query_params)

    return dict(
        spoken_topic_table_data=table_info[0],
        spoken_topic_table_pagination=table_info[1],
        spoken_topic_table_key=str(uuid.uuid4()),
        spoken_topic_table_selectedrowkeys=[],
    )


@app.callback(
    output=dict(
        spoken_topic_modal_type=Output(
            'spoken-topic-modal_type-store', 'data'
        ),
        spoken_topic_form_data=Output('spoken-topic-form-store', 'data'),
        spoken_topic_modal_visible=Output('spoken-topic-modal', 'visible'),
    ),
    inputs=dict(
        add_click=Input('spoken-topic-add', 'nClicks'),
        edit_click=Input({'type': 'spoken-topic-edit-operation', 'index': ALL}, 'nClicks'),
    ),
    state=dict(
        table_selected_rows=State('spoken-topic-list-table', 'selectedRows'),
    ),
    prevent_initial_call=True,
)
def open_spoken_topic_modal(add_click, edit_click, table_selected_rows):
    """
    打开新增/编辑话题弹窗回调
    """
    ctx.triggered_id = ctx.triggered_id if ctx.triggered_id is not None else {}
    if ctx.triggered_id == 'spoken-topic-add':
        return dict(
            spoken_topic_modal_type='add',
            spoken_topic_form_data=dict(
                status='0',
            ),
            spoken_topic_modal_visible=True,
        )
    elif isinstance(ctx.triggered_id, dict) and ctx.triggered_id.get('type') == 'spoken-topic-edit-operation':
        if not table_selected_rows:
            MessageManager.open_fail_message(content='请选择一行数据进行编辑')
            raise PreventUpdate
        edit_id = table_selected_rows[0]['topic_id']
        edit_data = get_spoken_topic_detail(edit_id)
        return dict(
            spoken_topic_modal_type='edit',
            spoken_topic_form_data=edit_data,
            spoken_topic_modal_visible=True,
        )

    raise PreventUpdate


@app.callback(
    output=dict(
        spoken_topic_modal_visible=Output('spoken-topic-modal', 'visible'),
        spoken_topic_table_key=Output('spoken-topic-list-table', 'key'),
    ),
    inputs=dict(
        confirm_click=Input('spoken-topic-confirm', 'nClicks'),
        cancel_click=Input('spoken-topic-cancel', 'nClicks'),
    ),
    state=dict(
        modal_type=State('spoken-topic-modal_type-store', 'data'),
        form_data=State('spoken-topic-form-store', 'data'),
    ),
    prevent_initial_call=True,
)
def save_spoken_topic(confirm_click, cancel_click, modal_type, form_data):
    """
    保存话题回调（新增/编辑）
    """
    if ctx.triggered_id == 'spoken-topic-cancel':
        return dict(
            spoken_topic_modal_visible=False,
            spoken_topic_table_key=no_update,
        )
    elif ctx.triggered_id == 'spoken-topic-confirm':
        # 表单验证
        if not form_data.get('topic_name'):
            MessageManager.open_fail_message(content='话题名称不能为空')
            raise PreventUpdate
        if not form_data.get('category_id'):
            MessageManager.open_fail_message(content='分类不能为空')
            raise PreventUpdate
        if not form_data.get('status'):
            MessageManager.open_fail_message(content='话题状态不能为空')
            raise PreventUpdate

        # 处理数据
        submit_data = {
            'topic_name': form_data.get('topic_name'),
            'category_id': form_data.get('category_id'),
            'status': form_data.get('status'),
        }
        if modal_type == 'edit':
            submit_data['topic_id'] = form_data.get('topic_id')

        try:
            if modal_type == 'add':
                add_spoken_topic(submit_data)
                MessageManager.open_success_message(content='新增成功')
            elif modal_type == 'edit':
                edit_spoken_topic(submit_data)
                MessageManager.open_success_message(content='编辑成功')

            return dict(
                spoken_topic_modal_visible=False,
                spoken_topic_table_key=str(uuid.uuid4()),
            )
        except Exception as e:
            MessageManager.open_fail_message(content=f'{modal_type}失败：{str(e)}')
            raise PreventUpdate

    raise PreventUpdate


@app.callback(
    output=dict(
        spoken_topic_delete_ids=Output('spoken-topic-delete-ids-store', 'data'),
        spoken_topic_delete_modal_visible=Output('spoken-topic-delete-modal', 'visible'),
    ),
    inputs=dict(
        delete_click=Input('spoken-topic-delete', 'nClicks'),
        operation_delete_click=Input({'type': 'spoken-topic-delete-operation', 'index': ALL}, 'nClicks'),
    ),
    state=dict(
        table_selected_rowkeys=State('spoken-topic-list-table', 'selectedRowKeys'),
    ),
    prevent_initial_call=True,
)
def open_spoken_topic_delete_modal(delete_click, operation_delete_click, table_selected_rowkeys):
    """
    打开删除话题弹窗回调
    """
    ctx.triggered_id = ctx.triggered_id if ctx.triggered_id is not None else {}
    if ctx.triggered_id == 'spoken-topic-delete' or (isinstance(ctx.triggered_id, dict) and ctx.triggered_id.get('type') == 'spoken-topic-delete-operation'):
        if not table_selected_rowkeys:
            MessageManager.open_fail_message(content='请选择至少一行数据进行删除')
            raise PreventUpdate

        return dict(
            spoken_topic_delete_ids=table_selected_rowkeys,
            spoken_topic_delete_modal_visible=True,
        )

    raise PreventUpdate


@app.callback(
    output=dict(
        spoken_topic_delete_modal_visible=Output('spoken-topic-delete-modal', 'visible'),
        spoken_topic_table_key=Output('spoken-topic-list-table', 'key'),
    ),
    inputs=dict(
        delete_confirm_click=Input('spoken-topic-delete-confirm', 'nClicks'),
        delete_cancel_click=Input('spoken-topic-delete-cancel', 'nClicks'),
    ),
    state=dict(
        delete_ids=State('spoken-topic-delete-ids-store', 'data'),
    ),
    prevent_initial_call=True,
)
def confirm_spoken_topic_delete(delete_confirm_click, delete_cancel_click, delete_ids):
    """
    确认删除话题回调
    """
    if ctx.triggered_id == 'spoken-topic-delete-cancel':
        return dict(
            spoken_topic_delete_modal_visible=False,
            spoken_topic_table_key=no_update,
        )
    elif ctx.triggered_id == 'spoken-topic-delete-confirm':
        try:
            delete_spoken_topic(','.join(delete_ids))
            MessageManager.open_success_message(content='删除成功')
            return dict(
                spoken_topic_delete_modal_visible=False,
                spoken_topic_table_key=str(uuid.uuid4()),
            )
        except Exception as e:
            MessageManager.open_fail_message(content=f'删除失败：{str(e)}')
            raise PreventUpdate

    raise PreventUpdate
