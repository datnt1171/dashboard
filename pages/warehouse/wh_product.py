import dash
from dash import html, dcc, dash_table, callback, Input, Output, ctx
import dash_bootstrap_components as dbc
import plotly.express as px


from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from utils import constants
from utils.query.wh.extract import get_mtd_factory_sales,get_table_value, get_mtd_product, get_sales_all
from utils.query.wh.extract import get_max_sales_date

dash.register_page(__name__, path="/wh_product")


# today = datetime.today().date()
# yesterday = today - timedelta(days=1)
# first_date = today.replace(day=1)

# same_day_last_month = yesterday - relativedelta(months=1)
# same_day_last_month_fisrt = same_day_last_month.replace(day=1)

today = get_max_sales_date()
yesterday = today #- timedelta(days=1)
first_date = today.replace(day=1)

same_day_last_month = yesterday - relativedelta(months=1)
same_day_last_month_fisrt = same_day_last_month.replace(day=1)

def layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2(id='wh_product_title')
            ],width=3, align='center'),

            dbc.Col([
                html.H6(["選擇要比較的時間段", html.Br(), "Chọn khoảng thời gian để so sánh"]),
                # Add DatePickerRange for target
                dcc.DatePickerRange(
                id='wh_product_date_range_target',
                start_date=same_day_last_month_fisrt,
                end_date=same_day_last_month,
                updatemode='bothdates',
                display_format=constants.date_format,

                )
            ]),

            dbc.Col([
                html.H6(["本月", html.Br(), "Tháng hiện tại"]),
                # Add DatePickerRange
                dcc.DatePickerRange(
                id='wh_product_date_range',
                start_date=first_date,
                end_date=yesterday,
                updatemode='bothdates',
                display_format=constants.date_format,
        
                )
            ]),

            dbc.Col([
                dbc.Row([
                    html.H6(f'更新資料到達 - Dữ liệu cập nhật đến ngày: {get_max_sales_date()}')
                ]),
                # dbc.Row([
                #     html.H6(f'更新於 - Cập nhật vào lúc: {max_import_wh_timestamp.date()}')
                # ])
            ], width=2, class_name='update_note'),

        ], style={'padding': '5px'}, class_name='filter_panel'),


        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.H5("数量差异 SỐ LƯỢNG CHÊNH LỆCH", style={'text-align':'center'}),
                    ])
                ]),

                dbc.Row([
                    dbc.Col([
                        dbc.RadioItems(
                            id="wh_product_radios_sort",
                            className="btn-group",
                            inputClassName="btn-check",
                            labelClassName="btn btn-outline-primary",
                            labelCheckedClassName="active",
                            options=[
                                {"label": "增加↑↑ - Tăng↑↑", "value": "increase"},
                                {"label": "減少↓↓ - Giảm↓↓", "value": "decrease"},
                            ],
                            value="increase",
                        ),
                    ])
                ]),

                dbc.Row([
                    dbc.Col([
                        dash_table.DataTable(
                            id='wh_product_table_sales_increase',
                            #sort_action='native',
                            style_cell={
                                'height': 'auto',
                                'width': '90px',
                                'whiteSpace': 'normal'
                            },
                            style_data_conditional=[
                                {
                                    "if": {"column_id": "数量差异 SỐ LƯỢNG CHÊNH LỆCH"}, 
                                    "backgroundColor": "#FFFF00",
                                    "pointerEvents": "none"  # Makes the row non-clickable
                                }
                            ]
                        ),
                    ],id='wh_product_row_sales_increase'),
                    

                    dbc.Col([
                            dash_table.DataTable(
                            id='wh_product_table_sales_decrease',
                            #sort_action='native',
                            style_cell={
                                'height': 'auto',
                                'width': '90px',
                                'whiteSpace': 'normal'
                            },
                            style_data_conditional=[
                                {
                                    "if": {"column_id": "数量差异 SỐ LƯỢNG CHÊNH LỆCH"}, 
                                    "backgroundColor": "#FFFF00",
                                    "pointerEvents": "none"  # Makes the row non-clickable
                                }
                            ]
                        ),
                    ], id='wh_product_row_sales_decrease')
                
                ])

            ], width=3, style={
                            'height': '500px',  # Set the height to create space for scrolling
                            'overflowY': 'scroll',  # Enable vertical scrolling
                            'borderRight': '1px solid #ddd',
                            'margin-top': '25px'
                            }),


            dbc.Col([

                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='wh_product_graph_increase')
                    ], width=6),

                    dbc.Col([
                        dcc.Graph(id='wh_product_graph_decrease')
                    ], width=6)
                ], style={'padding-top':'20px'}),

                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='wh_product_graph_total')
                    ])
                ]),

                dbc.Row([
                    dbc.Button("產品詳情增加/減少 - Chi tiết SP tăng/giảm", id='wh_product_btn_detail', outline=True,
                                color="info", className="me-1", n_clicks=0),
                ]),

                dbc.Row([
                    dash_table.DataTable(id='wh_product_table_detail',
                                        style_cell={
                                            'padding': '5px',
                                            'minWidth': '60px', 'maxWidth': '120px', 'whiteSpace': 'normal'  # Control column width
                                            },
                                        style_data={
                                            'whiteSpace': 'normal',  # Wrap text instead of adding extra space
                                            'height': 'auto',        # Allow the row height to adjust
                                            'lineHeight': '15px'     # Control line spacing
                                            },
                                        )
                ], id='wh_product_row_detail', style={"display": "none"}),

            ], width=9)
        ])

    ], fluid=True)

@callback(
    [Output('wh_product_table_sales_increase', 'data'),
     Output('wh_product_table_sales_increase', 'columns'),
     Output('wh_product_table_sales_decrease', 'data'),
     Output('wh_product_table_sales_decrease', 'columns')],

    [Input('wh_product_date_range', 'start_date'),
     Input('wh_product_date_range', 'end_date'),
     Input('wh_product_date_range_target', 'start_date'),
     Input('wh_product_date_range_target', 'end_date')]
)

def update_table_sales(start_date, end_date, start_date_target, end_date_target):

    # Convert to datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    start_date_target = datetime.strptime(start_date_target, '%Y-%m-%d')
    end_date_target = datetime.strptime(end_date_target, '%Y-%m-%d')


    df = get_mtd_factory_sales(start_date, end_date, start_date_target, end_date_target)
    df = df[['factory_name','quantity_diff']]
    df['quantity_diff'] = df['quantity_diff'].round(0)

    df.sort_values(by='quantity_diff', ascending=True, inplace=True)

    ### CHECK THIS AGAIN ###
    df.drop_duplicates(subset=['factory_name'], inplace=True) 
    ### CHECK THIS AGAIN ###
    new_column_names = {
        'factory_name': '客戶名称 TÊN KHÁCH HÀNG',
        'quantity_diff': '数量差异 SỐ LƯỢNG CHÊNH LỆCH',
    }
    df = df.rename(columns=new_column_names)


    columns = [{"name": i, "id": i} for i in df.columns]

    df_increase = df[df['数量差异 SỐ LƯỢNG CHÊNH LỆCH']>=1000]
    df_decrease = df[df['数量差异 SỐ LƯỢNG CHÊNH LỆCH']<=-1000]
    df_increase.sort_values(by='数量差异 SỐ LƯỢNG CHÊNH LỆCH', ascending=False, inplace=True)
    df_decrease.sort_values(by='数量差异 SỐ LƯỢNG CHÊNH LỆCH', ascending=True, inplace=True)
    
    return [df_increase.to_dict('records'), columns,
            df_decrease.to_dict('records'), columns]


@callback(
        [Output('wh_product_graph_increase', 'figure'),
        Output('wh_product_graph_decrease', 'figure'),
        Output('wh_product_graph_total', 'figure'),
        Output('wh_product_table_detail', 'data'),
        Output('wh_product_title', 'children'),],

        [Input('wh_product_date_range', 'start_date'),
        Input('wh_product_date_range', 'end_date'),
        Input('wh_product_date_range_target', 'start_date'),
        Input('wh_product_date_range_target', 'end_date'),
        Input('wh_product_table_sales_increase', 'active_cell'),
        Input('wh_product_table_sales_increase', 'data'),
        Input('wh_product_table_sales_decrease', 'active_cell'),
        Input('wh_product_table_sales_decrease', 'data'),]
)

def update_chart(start_date, end_date, start_date_target, end_date_target, active_cell_increase, table_data_increase, active_cell_decrease, table_data_decrease):

    if (active_cell_increase is None) & (active_cell_decrease is None):
        factory_name = '大森 TIM BER'
    else:
        triggered = ctx.triggered_id
        active_cell = active_cell_increase if triggered == "wh_product_table_sales_increase" else active_cell_decrease
        data = table_data_increase if triggered == "wh_product_table_sales_increase" else table_data_decrease
        factory_name = get_table_value(active_cell, data)


    # Convert to datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    start_date_target = datetime.strptime(start_date_target, '%Y-%m-%d')
    end_date_target = datetime.strptime(end_date_target, '%Y-%m-%d')


    df = get_mtd_product(start_date, end_date, start_date_target, end_date_target, factory_name)

    df['quantity_diff'] = df['total_quantity'] - df['total_quantity_prev']

    df.sort_values(by='quantity_diff', ascending=False, inplace=True)

    df_increase = df[df['quantity_diff']>0]
    df_increase = df_increase.head(5)

    df_decrease = df[df['quantity_diff']<0]
    df_decrease.sort_values(by='quantity_diff', ascending=True, inplace=True)
    df_decrease = df_decrease.head(5)

    df_sales_all = get_sales_all(start_date, end_date, factory_name)
    df_sales_all.sort_values('sales_quantity', inplace=True, ascending=True)
    df_sales_all = df_sales_all.tail(10)

    # Plot
    fig_increase = px.bar(df_increase, x='product_name', y='quantity_diff', text_auto=True)
    fig_increase.update_traces(marker_color='#339966', textposition='outside')
    max_y = df_increase['quantity_diff'].max() * 1.2  # Increase by 20%
    fig_increase.update_layout(yaxis_range=[0, max_y],
                                xaxis_title="產品名稱 - Tên SP",
                                yaxis_title="數量 - Số lượng",
                                yaxis=dict(tickformat=',.0f'),
                                title='產品增加 - Sản phẩm tăng', 
                                title_font=dict(size=24, color='black'),
                                title_x=0.5  # Center the title (0 is left, 0.5 is center, 1 is right)
                               )

    # Fig decrease
    fig_decrease = px.bar(df_decrease.sort_values(by='quantity_diff'), x='product_name', y='quantity_diff', text_auto=True)
    fig_decrease.update_traces(marker_color='#FF3333', textposition='outside')
    min_y = df_decrease['quantity_diff'].min() * 1.2  # Increase by 10%
    fig_decrease.update_layout(yaxis_range=[0, min_y],
                                xaxis_title="產品名稱 - Tên SP",
                                yaxis_title="數量 - Số lượng",
                                yaxis=dict(tickformat=',.0f'),
                                title='產品減少 - Sản phẩm giảm', 
                                title_font=dict(size=24, color='black'), 
                                title_x=0.5  # Center the title (0 is left, 0.5 is center, 1 is right)
                                )


    fig_sales_all = px.bar(df_sales_all, y='product_name', x='sales_quantity', text_auto=True, orientation='h')
    fig_sales_all.update_traces(textposition='outside')
    max_x_all = df_sales_all['sales_quantity'].max() * 1.1  # Increase by 10%
    fig_sales_all.update_layout(xaxis_range=[0, max_x_all], 
                                xaxis_title="數量 - Số lượng",
                                yaxis_title="產品名稱 - Tên SP",
                                xaxis=dict(tickformat='d'),
                                title='總銷售額 - SL bán hàng theo sản phẩm',
                                title_font=dict(size=24, color='black'), 
                                title_x=0.5  # Center the title (0 is left, 0.5 is center, 1 is right)
                                )

    df = df[['product_name','total_quantity','total_quantity_prev','quantity_diff']]
    new_column_names = {
        'product_name': f'產品名稱 - Tên SP',
        'total_quantity': f'{start_date.date()} 天到 {end_date.date()} 天的銷售額 - Bán hàng từ {start_date.date()} đến {end_date.date()}',
        'total_quantity_prev': f'{start_date_target.date()} 天到 {end_date_target.date()} 天的銷售額 - Bán hàng từ {start_date_target.date()} đến {end_date_target.date()}',
        'quantity_diff': '数量差异 SỐ LƯỢNG CHÊNH LỆCH',
    }
    df = df.rename(columns=new_column_names)

    warehouse_factory_title = f'購買詳情 - Chi tiết GH: {factory_name}'

    return [fig_increase, fig_decrease, fig_sales_all, df.to_dict('records'), warehouse_factory_title]

@callback(
        [Output('wh_product_row_sales_increase', 'style'),
         Output('wh_product_row_sales_decrease', 'style')],
        [Input('wh_product_radios_sort', 'value')]
)
def show_hide_table(radios_sort_factory):
    if (radios_sort_factory == 'increase'):
        return [{'display':'block'}, {'display':'none'}]
    elif (radios_sort_factory == 'decrease'):
        return [{'display':'none'}, {'display':'block'}]



@callback(
    Output("wh_product_row_detail", "style"),
    Input("wh_product_btn_detail", "n_clicks")
)
def toggle_table_visibility1(n_clicks):
    if n_clicks % 2 == 1:
        # Show table when n_clicks is odd
        return {"display": "block"}
    else:
        # Hide table when n_clicks is even
        return {"display": "none"}
    