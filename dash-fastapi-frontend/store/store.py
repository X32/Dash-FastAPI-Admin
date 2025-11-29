from dash import dcc, html


def render_store_container():
    return html.Div(
        [
            # 应用主题颜色存储容器
            dcc.Store(id='system-app-primary-color-container', data='#1890ff'),
            dcc.Store(
                id='custom-app-primary-color-container', storage_type='session'
            ),
            # token存储容器
            dcc.Store(id='token-container', storage_type='session'),
            # 当前路由存储容器
            dcc.Store(id='current-pathname-container'),
            # 路由列表存储容器
            dcc.Store(id='router-list-container'),
            # 确保所有在回调中使用的store容器都被正确定义
            dcc.Store(id='search-panel-data-container'),
        ]
    )
