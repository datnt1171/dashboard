import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

import pandas as pd
import numpy as np

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from utils.query.wh.extract import get_sales_same_month, get_mtd_by_month, get_text, get_color
from utils.query.wh.extract import get_max_sales_date
import plotly.graph_objects as go
from utils import constants

dash.register_page(__name__, path="/wh_conclusion")



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
                html.H1('结论 KẾT LUẬN')
            ], align='center'),

            dbc.Col([
                html.H6(["選擇要比較的時間段", html.Br(),"Chọn khoảng thời gian để so sánh"]),
                # Add DatePickerRange for target
                dcc.DatePickerRange(
                id='wh_conclusion_date_range_target',
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
                id='wh_conclusion_date_range',
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
            
        ], style={'padding':'5px'}, class_name='filter_panel'),


        dbc.Row([
            html.H3(id="wh_conclusion_title_order", className='conclusion-title'),
            html.H5(id="wh_conclusion_text_order_no_timber", className='conclusion-title'),
            html.H5(id="wh_conclusion_text_order", className='conclusion-title'),
            html.H3(id="wh_conclusion_title_sales", className='conclusion-title'),
            html.H5(id="wh_conclusion_text_sales_no_timber", className='conclusion-title'),
            html.H5(id="wh_conclusion_text_sales", className='conclusion-title')
        ]),


        dbc.Row([
            dbc.Col([], width=3), 

            dbc.Col([
                dcc.Graph(figure={}, id='wh_conclusion_graph')
            ], width=8) 
        ]),

    ])



@callback(
    [Output('wh_conclusion_title_order','children'),
     Output('wh_conclusion_text_order_no_timber','children'),
     Output('wh_conclusion_text_order_no_timber','style'),
     Output('wh_conclusion_text_order','children'),
     Output('wh_conclusion_text_order','style'),

     Output('wh_conclusion_title_sales','children'),
     Output('wh_conclusion_text_sales_no_timber','children'),
     Output('wh_conclusion_text_sales_no_timber','style'),
     Output('wh_conclusion_text_sales','children'),
     Output('wh_conclusion_text_sales','style'),
     
     Output('wh_conclusion_graph','figure')],
    
    [Input('wh_conclusion_date_range','start_date'),
     Input('wh_conclusion_date_range','end_date'),
     Input('wh_conclusion_date_range_target','start_date'),
     Input('wh_conclusion_date_range_target','end_date')]
)

def update_bar_sales(start_date, end_date, start_date_target, end_date_target):

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    start_date_target = datetime.strptime(start_date_target, '%Y-%m-%d')
    end_date_target = datetime.strptime(end_date_target, '%Y-%m-%d')

    # Group by same month
    df_sales_same_month = get_sales_same_month(start_date, end_date, start_date_target, end_date_target)
    df_sales_same_month = df_sales_same_month.pivot(index=['year','month'], columns='is_same_month', values='sum').reset_index()
    df_sales_same_month = df_sales_same_month.rename_axis(None, axis=1).reset_index(drop=True)

    # Selected
    df_sales = get_mtd_by_month(start_date.year, 
                                start_date.day, 
                                end_date.day, 
                                constants.EXCLUDE_FACTORY, 
                                'fact_sales', 
                                'sales_quantity',
                                'sales_date')

    df_order = get_mtd_by_month(start_date.year, 
                                start_date.day, 
                                end_date.day, 
                                constants.EXCLUDE_FACTORY, 
                                'fact_order', 
                                'order_quantity',
                                'order_date')

    
    df_sales = df_sales[df_sales['month'] == start_date.month]
    df_order = df_order[df_order['month'] == start_date.month]

    df_sales.columns = ['month','sales_quantity','sales_quantity_timber']
    df_order.columns = ['month','order_quantity','order_quantity_timber']

    
    # Target
    df_sales_target = get_mtd_by_month(start_date_target.year, 
                                start_date_target.day, 
                                end_date_target.day, 
                                constants.EXCLUDE_FACTORY, 
                                'fact_sales', 
                                'sales_quantity',
                                'sales_date')

    df_order_target = get_mtd_by_month(start_date_target.year, 
                                start_date_target.day, 
                                end_date_target.day, 
                                constants.EXCLUDE_FACTORY, 
                                'fact_order', 
                                'order_quantity',
                                'order_date')

    df_sales_target = df_sales_target[df_sales_target['month'] == start_date_target.month]
    df_order_target = df_order_target[df_order_target['month'] == start_date_target.month]

    df_sales_target.columns = ['month','sales_quantity','sales_quantity_timber']
    df_order_target.columns = ['month','order_quantity','order_quantity_timber']

    # Concat
    df_sales = pd.concat([df_sales,df_sales_target])
    df_order = pd.concat([df_order,df_order_target])
    df_all = df_sales_same_month.merge(df_sales, how='outer', on='month').merge(df_order, how='outer', on='month')
    df_all.fillna(0, inplace=True)


    
    df_all['total_sales'] = df_all['sales_quantity'] + df_all['sales_quantity_timber']
    df_all['total_order'] = df_all['order_quantity'] + df_all['order_quantity_timber']

    df_all.sort_values(by=['year','month'], inplace=True)
    df_all['month'] = df_all['month'].astype('str')
    df_all.reset_index(drop=True, inplace=True)

    df_all['pct_change_sales'] = df_all['total_sales'].pct_change()
    df_all['pct_change_sales_exclude'] = df_all['sales_quantity'].pct_change()
    df_all['pct_change_order'] = df_all['total_order'].pct_change()
    df_all['pct_change_order_exclude'] = df_all['order_quantity'].pct_change()

    order_no_timber_pct_change = round(df_all.loc[1,"pct_change_order_exclude"] * 100, 2)
    order_pct_change = round(df_all.loc[1,"pct_change_order"] * 100, 2)
    sales_no_timber_pct_change = round(df_all.loc[1,"pct_change_sales_exclude"] * 100, 2)
    sales_pct_change = round(df_all.loc[1,"pct_change_sales"] * 100, 2)

    # Text
    order_title = f'{start_date.month}月分的订单量与{start_date_target.year} 年{start_date_target.month}月相比 \
    ĐĐH THÁNG {start_date.month} SO VỚI THÁNG {start_date_target.month}/{start_date_target.year} （{start_date.day}日~{end_date.day}日）:'

    order_conclude_no_timber = f' • 沒有包含大森 KHÔNG BAO GỒM TIMBER: {get_text(order_no_timber_pct_change)} {order_no_timber_pct_change}%'
    order_conclude_no_timber_stype = {'color':get_color(order_no_timber_pct_change)}

    order_conclude = f' • 有包含大森 BAO GỒM CẢ TIMBER: {get_text(order_pct_change)} {order_pct_change}%'
    order_conclude_style = {'color':get_color(order_pct_change)}

    sales_title = f'{start_date.month}月分的送货量与{start_date_target.year}年{start_date_target.month}月相比 \
    GH THÁNG {start_date.month} SO VỚI THÁNG {start_date_target.month}/{start_date_target.year} （{start_date.day}日~{end_date.day}日）'

    sales_conclude_no_timber = f' • 沒有包含大森 KHÔNG BAO GỒM TIMBER: {get_text(sales_no_timber_pct_change)} {sales_no_timber_pct_change}%'
    sales_conclude_no_timber_style = {'color':get_color(sales_no_timber_pct_change)}

    sales_conclude = f' • 有包含大森 BAO GỒM CẢ TIMBER: {get_text(sales_pct_change)} {sales_pct_change}%'
    sales_conclude_style = {'color':get_color(sales_pct_change)}



    # Create the figure
    fig = go.Figure()

    # Add stacked bar traces
    fig.add_trace(
        go.Bar(
            x=df_all["month"],
            y=df_all["ĐĐH cũ"],
            name="本月內依訂單出貨 - SL giao theo ĐĐH cũ",
            marker_color="#FFCC99",
            text=df_all["ĐĐH cũ"].apply(lambda x: f"{x:,.0f}"),  # Add values as text
            textposition="inside",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_all["month"],
            y=df_all["ĐĐH trong tháng"],
            name="下單一個月內出貨 -SL giao theo ĐĐH trong tháng",
            marker_color="#FFB9B9",
            text=df_all["ĐĐH trong tháng"].apply(lambda x: f"{x:,.0f}"),  # Add values as text
            textposition="inside",
        )
    )

    # Add line traces
    fig.add_trace(
    go.Scatter(
            x=df_all["month"],
            y=df_all["total_order"],
            name="總訂單 - Tổng SL ĐĐH",
            mode="lines+markers+text",
            line=dict(color="red", width=2),
            text=df_all["total_order"].apply(lambda x: f"{x:,.0f}"),  # Add values as text
            textposition='top right',
            textfont=dict(color="red")
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_all["month"],
            y=df_all["total_sales"],
            name="總銷售額 - Tổng SL Giao Hàng",
            mode="lines+markers+text",
            line=dict(color="green", width=2),
            text=df_all["total_sales"].apply(lambda x: f"{x:,.0f}"),  # Add values as text
            textposition='top left',  # Adjust text position dynamically
            textfont=dict(color="green")
        )
    )

    # Update layout for better readability
    fig.update_layout(
        xaxis=dict(title="月 - Tháng"),
        yaxis=dict(title="數量 - Số lượng",
                   tickformat=',.0f'),
        barmode="stack",
        legend=dict(title=""),
        template="plotly_white",
    )
    fig.update_xaxes(
            tickmode="linear",      # Set tick mode to linear for even spacing
            dtick="M1"              # Set tick interval to 1 month
        )


    return [order_title, order_conclude_no_timber, order_conclude_no_timber_stype, order_conclude, order_conclude_style,
            sales_title, sales_conclude_no_timber,sales_conclude_no_timber_style, sales_conclude, sales_conclude_style,
            fig]