import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from utils.query.wh.extract import get_factory_list, get_mtd_by_month, get_factory_code
from utils.query.wh.extract import get_max_sales_date
from utils import constants

dash.register_page(__name__, path="/wh_plan")


factory_list = get_factory_list()
def layout():
    return dbc.Container([
        dbc.Row([

            dbc.Col([
                html.H6("選擇客戶 - Chọn KH"),
                dcc.Dropdown(id='wh_plan_dropdown_factory' ,
                            options=factory_list['factory_name'], 
                            value='大森 TIM BER',
                            clearable=False,)
            ], width=2),

            dbc.Col([
                html.H6("今年 - Năm hiện tại"), #Target Year 
                dcc.Dropdown(options=constants.LIST_YEAR, # Year Option
                            value=2025,
                            id='wh_plan_selected_year',
                            clearable=False)
            ], width=2),

            dbc.Col([
                html.H1(id='wh_plan_title', style={'text-align':'center'})
            ]),

            dbc.Col([
                dbc.Row([
                    html.H6(f'更新資料到達 - Dữ liệu cập nhật đến ngày: {get_max_sales_date()}')
                ]),
                # dbc.Row([
                #     html.H6(f'更新於 - Cập nhật vào lúc: {max_import_wh_timestamp.date()}')
                # ])
            ], width=2, class_name='update_note'),
        ],style={'padding-top':'5px'}, class_name='filter_panel'),

        dbc.Row([
            dbc.Col([
                dcc.Graph(figure={}, id='wh_plan_graph_percent')
            ])
        ]),
    
    ])

@callback(
    Output('wh_plan_title','children'),
    Input('wh_plan_dropdown_factory', 'value')
)
def update_title(factory_name):
    return f'計劃及實際銷售 - Dự định GH và GH thực tế {factory_name}'


@callback(
    [Output('wh_plan_graph_percent', 'figure'),],
    [Input('wh_plan_dropdown_factory', 'value'),
     Input('wh_plan_selected_year','value')]
)

def update_bar_plan(factory_name, selected_year):
    factory_code = get_factory_code(factory_name)
    # Get sales
    df_sales = get_mtd_by_month(selected_year, 1, 31, factory_code, "fact_sales", "sales_quantity", "sales_date")
    df_sales.columns = ['month','sales_quantity','sales_quantity_timber']
    df_sales.drop(columns = ['sales_quantity'], inplace=True)

    # Get planned deliveries
    df_plan  = get_mtd_by_month(selected_year, 1, 31, factory_code, "fact_order", "order_quantity", "estimated_delivery_date")
    df_plan.columns = ['month','plan_quantity','plan_quantity_timber']
    df_plan.drop(columns = ['plan_quantity'], inplace=True)

    # Merge for plotting
    df = df_sales.merge(df_plan, on='month', how='outer')
    df.columns = ['month','sales_quantity','plan_quantity']

    df.fillna(0,inplace=True)

    df['percentage'] = df['sales_quantity'] / df['plan_quantity'] * 100

    fig = go.Figure()

    # Add bars for estimated sales
    fig.add_trace(go.Bar(
        x=df['month'],
        y=df['plan_quantity'],
        name='預計銷售額 - Dự định GH',
        marker_color='#7AB2D3',
        text=df['plan_quantity'].apply(lambda x: f"{x:,.0f}"),
        textposition='outside'
    ))

    # Add bars for actual sales
    fig.add_trace(go.Bar(
        x=df['month'],
        y=df['sales_quantity'],
        name='實際銷售額 - GH Thực tế',
        marker_color='#72BF78',
        text=df['sales_quantity'].apply(lambda x: f"{x:,.0f}"),
        textposition='outside'
    ))

    # Filter out rows where percentage is 0
    df_filtered = df[df['percentage'] > 0]

    # Add line for percentage (on secondary y-axis) only for non-zero values
    fig.add_trace(go.Scatter(
        x=df_filtered['month'],
        y=df_filtered['percentage'],
        name='%達到率 - %Tỉ lệ đại được',
        yaxis='y2',
        mode='lines+markers+text',
        marker=dict(color='red', size=10),
        line=dict(color='red'),
        text=[f'{p:.1f}%' for p in df_filtered['percentage']],
        textposition='middle right',
        textfont=dict(size=14, color='red')
    ))

    max_percentage = df['percentage'].max()
    y2_upper_limit = max(max_percentage * 1.1, 100)  # Add a 10% buffer, minimum of 100%

    # Update layout
    fig.update_layout(
        #title='',
        xaxis_title='月 - Tháng',
        yaxis_title='數量 - Số lượng',
        yaxis2=dict(
            title='Percentage (%)',
            overlaying='y',  # Overlay with the primary y-axis
            side='right',  # Position it on the right side
            range=[0, y2_upper_limit],  # Set range from 0 to 100 for percentage
        ),
        title_x=0.5,
        barmode='group',  # Group the bars side by side
        yaxis=dict(
            tickformat=',.0f'  # This removes the comma from the numbers
            ),
        height=500
    )

    fig.update_xaxes(
            tickmode="linear",      # Set tick mode to linear for even spacing
            dtick="M1"              # Set tick interval to 1 month
        )

    return [fig]