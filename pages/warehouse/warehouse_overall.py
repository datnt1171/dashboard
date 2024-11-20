import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

from datetime import datetime
from extract import get_overall_order, get_overall_sales, extract_order_target, extract_sales_target
from transform import col_to_date, filter_selected_day

from plot_fig import plot_sales_order_target

import constants

dash.register_page(__name__, path="/warehouse_overall")

layout = dbc.Container([
    dbc.Row([

        dbc.Col([
            html.H6("選擇日期範圍 - Chọn khoảng thời gian"), #Select day range
            # Add DatePickerRange
            dcc.RangeSlider(1, 31, 1, value=[1, 31], id='day_slicer_month'),
        ], width=6),

        dbc.Col([
            html.H6("目標月份 - Tháng mục tiêu"), #Target month
            dcc.Dropdown(options=constants.LIST_MONTH, # Month Option
                         value=5,
                         id='target_month',
                         clearable=False),
        ], width=2),

        dbc.Col([
            html.H6("目標年 - Năm mục tiêu"), #Target Year 
            dcc.Dropdown(options=constants.LIST_YEAR, # Year Option
                         value=2022,
                         id='target_year',
                         clearable=False)
        ], width=2)
    ], style={'padding':'5px'}),
    
    dbc.Row([
        html.H2(id='weekly_title_tw'),
        html.H2(id='weekly_title_vn'),
    ], style={'padding-top':'10px'}),

    dbc.Row([
        html.Img(id='bar-graph-matplotlib')
    ]),

])



@callback(
    [Output('bar-graph-matplotlib', 'src'),
     Output('weekly_title_tw','children'),
     Output('weekly_title_vn','children'),
    ],
    
    [Input('day_slicer_month','value'),
     Input('target_month','value'),
     Input('target_year','value')]
)

def update_bar_sales(day_range, target_month, target_year):
    # Get data
    ## order_all
    df_order = get_overall_order(datetime.today().date().year)

    ## sales_all
    df_sales = get_overall_sales(datetime.today().date().year)

    ## order target
    order_target = extract_order_target(day_range, target_month, target_year)

    ## sales target
    sales_target = extract_sales_target(day_range, target_month, target_year)

    # Preprocessing
    ## To datetime
    df_order = col_to_date(df_order, ['order_date'])
    df_sales = col_to_date(df_sales, ['sales_date'])


    ## Filter the day range from user input
    df_order = filter_selected_day(df_order, 'order_date', day_range)
    df_sales = filter_selected_day(df_sales, 'sales_date', day_range)


    ## Get month
    df_order['month'] = df_order['order_date'].dt.month
    df_sales['month'] = df_sales['sales_date'].dt.month


    ## Separate to Timber and Remain data
    ### order
    df_order_remain = df_order[df_order['factory_code']!='30673']
    df_order_timber = df_order[df_order['factory_code']=='30673']
    ### sales
    df_sales_remain = df_sales[df_sales['factory_code']!='30673']
    df_sales_timber = df_sales[df_sales['factory_code']=='30673']


    ## Aggregate by month
    df_order_remain_grouped = df_order_remain.groupby('month').agg({'order_quantity':'sum'}).reset_index()
    df_order_timber_grouped = df_order_timber.groupby('month').agg({'order_quantity':'sum'}).reset_index()

    df_sales_remain_grouped = df_sales_remain.groupby('month').agg({'sales_quantity':'sum'}).reset_index()
    df_sales_timber_grouped = df_sales_timber.groupby('month').agg({'sales_quantity':'sum'}).reset_index()


    # Merge for plotting
    df = df_sales_remain_grouped.merge(df_sales_timber_grouped, on='month', how='outer')
    df = df.merge(df_order_remain_grouped, on='month', how='outer')
    df = df.merge(df_order_timber_grouped, on='month', how='outer')

    # Rename to avoid duplicate name
    df.columns = ['month','sales_quantity','sales_quantity_timber','order_quantity','order_quantity_timber']
    df.fillna(0, inplace=True)
    df['sales_target%'] = df['sales_quantity'] / sales_target
    df['order_target%'] = df['order_quantity'] / order_target
    fig_bar_matplotlib = plot_sales_order_target(df, target_year, target_month)

    title_tw = f"2024年每月送貨比较与{target_year}年{target_month}月相比 （每月{day_range[0]}日~{day_range[1]}日）"
    title_vn = f"SO SÁNH SỐ LƯỢNG GIAO HÀNG MỖI THÁNG SO VỚI THÁNG {target_month} NĂM {target_year}"
    return [fig_bar_matplotlib, title_tw, title_vn]