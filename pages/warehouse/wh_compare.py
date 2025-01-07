import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

import constants
from extract import  get_factory_list, get_product_list, get_compare_sales_data
from extract import get_max_sales_date

# Get data

dash.register_page(__name__, path="/wh_compare")


factory_list = get_factory_list()
product_list = get_product_list()
def layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([],width=3),
            dbc.Col([
                html.H2("按年份比較交貨 - So sánh SL giao hàng theo từng năm"),
            ]),
            
            dbc.Col([
                dbc.Row([
                    html.H6(f'更新資料到達 - Dữ liệu cập nhật đến ngày: {get_max_sales_date()}')
                ]),
                # dbc.Row([
                #     html.H6(f'更新於 - Cập nhật vào lúc: {max_import_wh_timestamp.date()}')
                # ])
            ], width=2, class_name='update_note'),
        ], class_name='filter_panel'),

        dbc.Row([
            dbc.Col([
                dbc.Row([
                    html.H6("選擇客戶 - Chọn KH"),
                    dcc.Dropdown(id='wh_compare_dropdown_factory',
                                    options=factory_list['factory_name'].unique().tolist() + ['全部 - Tất cả'], 
                                    value='全部 - Tất cả',
                                    clearable=False,)
                ], style={'padding': "60px 0px 10px 0px"}),

                dbc.Row([
                    html.H6("選擇產品 - Chọn SP"),
                    dcc.Dropdown(id='wh_compare_dropdown_product',
                                    options=product_list['product_name'].unique().tolist() + ['全部 - Tất cả'], 
                                    value='全部 - Tất cả',
                                    clearable=False,)
                ], style= {'padding-bottom': '10px'}),

                # dbc.Row([
                #     html.H6("Bán hàng/Đặt hàng"),
                #     dcc.Checklist(id='checklist_sales_order',
                #              options=[
                #                 {'label': 'Sales', 'value': 'sales'},
                #                 {'label': 'Order', 'value': 'order'},
                #                 ],
                #              value=['sales'],
                #              inline=True),
                # ]),

                dbc.Row([
                    html.H6("選擇年份 - Chọn năm"),
                    dcc.Dropdown(id='wh_compare_dropdown_year',
                            options=constants.LIST_YEAR,
                            value=[2024,2023],
                            multi=True,
                            clearable=False
                    )
                ], style= {'padding-bottom': '10px'}),

                dbc.Row([
                    html.H6('分組依據 - Nhóm theo'),
                    dcc.Dropdown(
                        id="wh_compare_dropdown_groupby",
                        options=[
                            {"label": "四分之一 Quý", "value": "quarter"},
                            {"label": "月 Tháng", "value": "month"},
                            {"label": "星期 Tuần", "value": "week_of_year"},
                            {"label": "天 Ngày", "value": "date"},
                        ],
                        value="month",
                        clearable=False
                    ),
                ], style= {'padding-bottom': '10px'}),



            ], id='wh_compare_sidebar', width=2),


            dbc.Col([
                dbc.Row([
                    dcc.Graph(figure={}, id='wh_compare_timeseries')
                ]),

                # dbc.Row([
                #     dcc.Graph(figure={}, id='line_by_time_concat')
                # ])
                
            ], width=10),


        ]),

    ], fluid=True)

@callback(
    Output('wh_compare_timeseries', 'figure'),
    [
        Input('wh_compare_dropdown_factory', 'value'),
        Input('wh_compare_dropdown_product', 'value'),
        Input('wh_compare_dropdown_year', 'value'),
        Input('wh_compare_dropdown_groupby', 'value'),
    ]
)

def update_line_chart(factory_name, product_name, list_year, time_groupby):
    if len(list_year)==0:
        return {}

    df_sales_stack = get_compare_sales_data(factory_name, product_name, list_year, time_groupby)
    df_sales_stack.rename(columns={'agg_col':time_groupby}, inplace=True)
    if time_groupby == 'date':
        sales_fig_stack = px.line(df_sales_stack,
                              x=time_groupby,
                              y='sales_quantity',
                              color="year")
    else:
        sales_fig_stack = px.line(df_sales_stack,
                                x=time_groupby,
                                y='sales_quantity',
                                color="year",
                                text=df_sales_stack['sales_quantity'].apply(lambda x: f"{x:,.0f}"),
                                symbol="year")
        
        sales_fig_stack.update_traces(
        textposition="top center",
        selector=dict(mode="lines+markers+text"),
        )
        for trace in sales_fig_stack.data:
            trace["textfont"] = dict(color=trace["line"]["color"])  # Set text color to match line color
    
    sales_fig_stack.update_xaxes(
        tickmode="linear",      # Set tick mode to linear for even spacing
        dtick="M1"              # Set tick interval to 1 month
    )
    x_axis_title_map = {"quarter": '四分之一 - Quý',
                        'month': '月 - Tháng',
                        'week_of_year': '星期 - Tuần',
                        'date': '天 - Ngày'}
    sales_fig_stack.update_layout(
    xaxis=dict(title=x_axis_title_map[time_groupby]),
    yaxis=dict(title="數量 - Số lượng",
                tickformat=',.0f'),
    legend=dict(title="年 Năm")

    )
    return sales_fig_stack