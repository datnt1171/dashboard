import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

import numpy as np

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from extract import get_sales_same_month, get_order_same_month, get_text, get_color
from transform import col_to_date
from extract import get_max_sales_date
import plotly.graph_objects as go
import constants

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

    df_sales = get_sales_same_month(start_date, end_date, start_date_target, end_date_target)
    df_sales = col_to_date(df_sales, ['sales_date','order_date'])
    df_sales['is_same_month'] = np.where(df_sales['sales_date'].dt.month == df_sales['order_date'].dt.month, 'ĐĐH trong tháng', 'ĐĐH cũ')
    df_sales['month'] = df_sales['sales_date'].dt.month

    df_sales_no_timber = df_sales[df_sales['factory_code'] != '30673']
    df_sales_no_timber_grouped = df_sales_no_timber.groupby('month').agg({'sales_quantity':'sum'})
    df_sales_no_timber_grouped['diff'] = df_sales_no_timber_grouped['sales_quantity'].diff()
    df_sales_no_timber_grouped['pct_change'] = df_sales_no_timber_grouped['sales_quantity'].pct_change()

    df_sales_grouped = df_sales.groupby('month').agg({'sales_quantity':'sum'})
    df_sales_grouped['diff'] = df_sales_grouped['sales_quantity'].diff()
    df_sales_grouped['pct_change'] = df_sales_grouped['sales_quantity'].pct_change()

    df_order = get_order_same_month(start_date, end_date, start_date_target, end_date_target)
    df_order = col_to_date(df_order, ['order_date'])
    df_order['month'] = df_order['order_date'].dt.month

    df_order_no_timber = df_order[df_order['factory_code'] != '30673']
    df_order_no_timber_grouped = df_order_no_timber.groupby('month').agg({'order_quantity':'sum'})
    df_order_no_timber_grouped['diff'] = df_order_no_timber_grouped['order_quantity'].diff()
    df_order_no_timber_grouped['pct_change'] = df_order_no_timber_grouped['order_quantity'].pct_change()

    df_order_grouped = df_order.groupby('month').agg({'order_quantity':'sum'}).reset_index()
    df_order_grouped['diff'] = df_order_grouped['order_quantity'].diff()
    df_order_grouped['pct_change'] = df_order_grouped['order_quantity'].pct_change()

    df_same_month_grouped = df_sales.groupby(['month','is_same_month']).agg({'sales_quantity':'sum'}).reset_index()
    df_same_month_grouped = df_same_month_grouped.pivot(index='month',
                                                    columns='is_same_month',
                                                    values='sales_quantity').reset_index()
    df_all = df_same_month_grouped[['month','ĐĐH cũ','ĐĐH trong tháng']].merge(df_order_grouped[['month','order_quantity']],
                                                                           on='month', how='left')
    df_all['sales_quantity'] = df_all['ĐĐH cũ'] + df_all['ĐĐH trong tháng']
    
    for df in [df_order_no_timber_grouped, df_order_grouped, df_sales_no_timber_grouped, df_sales_grouped]:
        df.fillna(0, inplace=True)
    order_no_timber_pct_change = round(df_order_no_timber_grouped.iloc[-1,-1] * 100, 2)
    order_pct_change = round(df_order_grouped.iloc[-1,-1] * 100, 2)
    sales_no_timber_pct_change = round(df_sales_no_timber_grouped.iloc[-1,-1] * 100, 2)
    sales_pct_change = round(df_sales_grouped.iloc[-1,-1] * 100, 2)

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
        y=df_all["order_quantity"],
        name="總訂單 - Tổng SL ĐĐH",
        mode="lines+markers+text",
        line=dict(color="red", width=2),
        text=df_all["order_quantity"].apply(lambda x: f"{x:,.0f}"),  # Add values as text
        textposition='top right',
        textfont=dict(color="red")
    )
)
    fig.add_trace(
        go.Scatter(
            x=df_all["month"],
            y=df_all["sales_quantity"],
            name="總銷售額 - Tổng SL Giao Hàng",
            mode="lines+markers+text",
            line=dict(color="green", width=2),
            text=df_all["sales_quantity"].apply(lambda x: f"{x:,.0f}"),  # Add values as text
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