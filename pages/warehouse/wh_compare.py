import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

import constants
from extract import  get_overall_sales, get_factory_list, get_product_list
from global_variable import max_sales_date

# Get data

dash.register_page(__name__, path="/wh_compare")


factory_list = get_factory_list()
product_list = get_product_list()
layout = dbc.Container([
    dbc.Row([
        dbc.Col([],width=3),
        dbc.Col([
            html.H2("按年份比較交貨 - So sánh SL giao hàng theo từng năm"),
        ]),
        
        dbc.Col([
            dbc.Row([
                html.H6(f'更新資料到達 - Dữ liệu cập nhật đến ngày: {max_sales_date}')
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
                        {"label": "天 Ngày", "value": "day_of_year"},
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
    [Output('wh_compare_timeseries','figure'),
     ],
    #Output('line_by_time_concat','figure')
    [Input('wh_compare_dropdown_factory','value'),
     Input('wh_compare_dropdown_product','value'),
     #Input('checklist_sales_order','value'),
     Input('wh_compare_dropdown_year','value'),
     Input('wh_compare_dropdown_groupby','value'),
     ]
)

def update_line_chart(factory_name, product_name, list_year, time_groupby):
    if len(list_year)==0:
        return [{}]#, {}] # Empty fig

    df_sales = get_overall_sales(list_year)
    df_sales = df_sales.merge(factory_list, on='factory_code', how='left')

    if factory_name != '全部 - Tất cả':
        df_sales = df_sales[df_sales['factory_name']==factory_name]
    if product_name != '全部 - Tất cả':
        df_sales = df_sales[df_sales['product_name']==product_name]


    df_sales['sales_date'] = pd.to_datetime(df_sales['sales_date'])

    # Stacked
    df_sales['year'] = df_sales['sales_date'].dt.year
    df_sales['quarter'] = df_sales['sales_date'].dt.quarter
    df_sales['month'] = df_sales['sales_date'].dt.month
    df_sales['week_of_year'] = df_sales['sales_date'].dt.isocalendar().week
    df_sales['day_of_year'] = df_sales['sales_date'].dt.dayofyear
    
    

    df_sales_stack = df_sales.groupby(["year",time_groupby]).agg({'sales_quantity':'sum'}).reset_index()
    if time_groupby == 'day_of_year':
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
                        'day_of_year': '一年中的某一天 - Ngày trong năm'}
    sales_fig_stack.update_layout(
    xaxis=dict(title=x_axis_title_map[time_groupby]),
    yaxis=dict(title="數量 - Số lượng",
                tickformat=',.0f'),
    legend=dict(title="年 Năm")

    )
    
    # #Concat
    # concat_map = {'quarter':'Q',
    #               'month':'M',
    #               'week_of_year':'W',
    #               'day_of_year':'D'}
    
    # groupby = concat_map[time_groupby]
    # df_sales['time_period'] = df_sales['sales_date'].dt.to_period(groupby)
    # # Aggregate sales_quantity by month
    # df_grouped = df_sales.groupby('time_period', as_index=False)['sales_quantity'].sum()

    # # Convert period to datetime for Plotly compatibility
    # df_grouped['time_period'] = df_grouped['time_period'].dt.to_timestamp()
    # df_grouped['year'] = df_grouped['time_period'].dt.year

    # # Create the line chart
    # sales_fig_concat = px.line(
    #     df_grouped,
    #     x='time_period',
    #     y='sales_quantity',
    #     color='year',
    #     # title='Monthly Sales Quantity Over Time',
    #     # labels={'year_month': 'Month', 'sales_quantity': 'Sales Quantity'}
    # )
    

    # if time_groupby != "day_of_year":
    #     sales_fig_stack.update_xaxes(
    #     tickmode="linear",
    #     )
    #     sales_fig_concat.update_xaxes(
    #     tickformat="%m-%Y",     # Format to show month and year (e.g., "Jan 2021")
    #     tickmode="linear",      # Set tick mode to linear for even spacing
    #     dtick="M1"              # Set tick interval to 1 month
    #     )


    return [sales_fig_stack]#, sales_fig_concat]