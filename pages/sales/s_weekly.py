import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np

import constants
from extract import  get_overall_sales, get_factory_list
dash.register_page(__name__, path="/s_weekly")


factory_list = get_factory_list()
def layout():
    return dbc.Container([
    dbc.Row([
        dbc.Col([
                html.H6("選擇客戶 - Chọn KH"),
                dcc.Dropdown(id='s_weekly_dropdown_factory',
                            options=factory_list['factory_name'].unique().tolist() + ['全部 - Tất cả'], 
                            value='全部 - Tất cả',
                            clearable=False,)
        ],width=2),

        dbc.Col([
            html.H2("按月收入 - Doanh thu theo từng tháng"),
        ]),
        

    ], class_name='filter_panel'),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='s_weekly_annual_revenue', figure={}) 
        ], width=4),

        dbc.Col([
            dcc.Graph(id='s_weekly_monthly_revenue', figure={})
        ],width=8),
    ]),

    dbc.Row([
        dcc.Graph(id='s_weekly_daily_revenue', figure={})
    ])

], fluid=True)

@callback(
    [Output('s_weekly_annual_revenue','figure')],
    [Input('s_weekly_dropdown_factory','value')]
)

def update_annual_revenue(factory_name):

    df_sales = get_overall_sales([2017,2018,2019,2020,2021,2022,2023,2024])
    df_sales = df_sales.merge(factory_list, on='factory_code', how='left')

    if factory_name != '全部 - Tất cả':
        df_sales = df_sales[df_sales['factory_name']==factory_name]

    df_sales['sales_date'] = pd.to_datetime(df_sales['sales_date'])

    # Stacked
    df_sales['year'] = df_sales['sales_date'].dt.year
    
    df_sales_stack = df_sales.groupby('year').agg({'sales_quantity':'sum'}).reset_index()
    
    sales_fig_stack = px.bar(df_sales_stack, 
                             x='year', 
                             y='sales_quantity',
                             title="Annual Revenue",
                             text_auto=True,
                             )
    
    sales_fig_stack.update_traces(textposition="outside")
    return [sales_fig_stack]

@callback(
    [Output('s_weekly_monthly_revenue','figure'),
     Output('s_weekly_daily_revenue','figure')],
    [Input('s_weekly_dropdown_factory','value'),
     Input('s_weekly_annual_revenue','clickData')]
)

def update_monthly_revenue(factory_name, clickData):
    
    if clickData is None:
        year = 2024
    else:
        year = clickData['points'][0]['x']
    df_sales = get_overall_sales(year)
    df_sales = df_sales.merge(factory_list, on='factory_code', how='left')

    if factory_name != '全部 - Tất cả':
        df_sales = df_sales[df_sales['factory_name']==factory_name]
    
    df_sales['sales_date'] = pd.to_datetime(df_sales['sales_date'])
    df_sales['month'] = df_sales['sales_date'].dt.month
    df_sales['week_of_year'] = df_sales['sales_date'].dt.isocalendar().week

    df_sales_stack = df_sales.groupby(['month','week_of_year']).agg({'sales_quantity':'sum'}).reset_index()
    df_sales_stack['week_of_year'] = np.where((df_sales_stack['month'] == 12) & (df_sales_stack['week_of_year'] == 1),
                                          53,df_sales_stack['week_of_year'])
    df_sales_stack['week_of_year'] = np.where((df_sales_stack['month'] == 1) & (df_sales_stack['week_of_year'] > 10),
                                          1,df_sales_stack['week_of_year'])
    
    min_weeks = df_sales_stack.groupby(['month'])['week_of_year'].min().reset_index()
    min_weeks.rename(columns={'week_of_year': 'min_week_of_month'}, inplace=True)
    df_sales_stack = df_sales_stack.merge(min_weeks, on=['month'], how='left')
    df_sales_stack['week_of_month'] = df_sales_stack['week_of_year'] - df_sales_stack['min_week_of_month'] + 1

    sales_fig_stack = px.bar(df_sales_stack, 
                             x='month', 
                             y='sales_quantity', 
                             color='week_of_month',
                             title='Revenue by month and week',
                             text_auto=True)
    sales_fig_stack.update_traces(textposition="outside")

    df_sales_line = df_sales.groupby('sales_date').agg({'sales_quantity':'sum'}).reset_index()

    line_daily = px.line(df_sales_line, 
                         x='sales_date', 
                         y='sales_quantity',
                         title='Daily revenue')

    return [sales_fig_stack, line_daily]