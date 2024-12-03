import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from extract import get_factory_list, get_overall_sales, get_overall_planned
from global_variable import max_sales_date

dash.register_page(__name__, path="/wh_plan")


factory_list = get_factory_list()
layout = dbc.Container([

    dbc.Row([

        dbc.Col([
            html.H6("選擇客戶 - Chọn KH"),
            dcc.Dropdown(id='wh_plan_dropdown_factory' ,
                         options=factory_list['factory_name'], 
                         value='大森 TIM BER',
                         clearable=False,)
        ], width=2),

        dbc.Col([
            html.H1(id='wh_plan_title', style={'text-align':'center'})
        ]),

        dbc.Col([
            dbc.Row([
                html.H6(f'更新資料到達 - Dữ liệu cập nhật đến ngày: {max_sales_date}')
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
    [Input('wh_plan_dropdown_factory', 'value')]
)

def update_bar_plan(factory_name):

    # Get sales
    df_sales = get_overall_sales(datetime.today().date().year)
    # Get planned deliveries
    df_plan = get_overall_planned(datetime.today().date().year)

    # Preprocessing
    df_sales['sales_date'] = pd.to_datetime(df_sales['sales_date'])
    df_plan['estimated_delivery_date'] = pd.to_datetime(df_plan['estimated_delivery_date'])

    ## Join with factory_name to filter
    df_sales = df_sales.merge(factory_list, on='factory_code', how='left')
    df_plan = df_plan.merge(factory_list, on='factory_code', how='left')

    ## Filter selected company
    df_sales = df_sales[df_sales['factory_name']==factory_name]
    df_plan = df_plan[df_plan['factory_name']==factory_name]

    ## Sales
    df_sales['month'] = df_sales['sales_date'].dt.month
    df_sales_grouped = df_sales.groupby('month').agg({'sales_quantity': 'sum'}).reset_index()

    ## Plan
    df_plan['month'] = df_plan['estimated_delivery_date'].dt.month
    df_plan_grouped = df_plan.groupby('month').agg({'order_quantity': 'sum'}).reset_index()


    # Merge for plotting
    df = df_sales_grouped.merge(df_plan_grouped, on='month', how='left')
    df.columns = ['month','sales_quantity','plan_quantity']

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

    # Add line for percentage (on secondary y-axis)
    fig.add_trace(go.Scatter(
        x=df['month'],
        y=df['percentage'],
        name='%達到率 - %Tỉ lệ đại được',
        yaxis='y2',
        mode='lines+markers+text',
        marker=dict(color='red', size=10),
        line=dict(color='red'),
        text=[f'{p:.1f}%' for p in df['percentage']],  # Display as percentage with 1 decimal
        textposition='middle right',
        textfont=dict(
            size=14,       # Set font size
            color='red'   # Set font color
        )
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