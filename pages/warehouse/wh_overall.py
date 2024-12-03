import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

from datetime import datetime

from extract import get_overall_order, get_overall_sales, extract_order_target, extract_sales_target
from transform import col_to_date, filter_selected_day
from plot_fig import plot_sales_order_target
from global_variable import max_sales_date
import constants


dash.register_page(__name__, path="/wh_overall")


layout = dbc.Container([
    dbc.Row([

        dbc.Col([
            dbc.Row([
                html.H6("選擇日期範圍 - Chọn khoảng thời gian"), #Select day range
                # Add RangeSlider
                dcc.RangeSlider(1, 31, 1,
                                value=[1, max_sales_date.day], 
                                id='wh_overall_day_slicer',
                                marks={i: {'label': str(i), 'style': {'color': 'gray' if i > max_sales_date.day else 'black'}} for i in range(1, 32)},),
            ]),
        ], width=5),

        dbc.Col([
            html.H6("目標月份 - Tháng mục tiêu"), #Target month
            dcc.Dropdown(options=constants.LIST_MONTH, # Month Option
                         value=5,
                         id='wh_overall_target_month',
                         clearable=False),
        ], width=2),

        dbc.Col([
            html.H6("目標年 - Năm mục tiêu"), #Target Year 
            dcc.Dropdown(options=constants.LIST_YEAR, # Year Option
                         value=2022,
                         id='wh_overall_target_year',
                         clearable=False)
        ], width=2),

        dbc.Col([
            dbc.Row([
                html.H6(f'更新資料到達 - Dữ liệu cập nhật đến ngày: {max_sales_date}')
            ]),
            # dbc.Row([
            #     html.H6(f'更新於 - Cập nhật vào lúc: {max_import_wh_timestamp.date()}')
            # ])
        ], width=2, class_name='update_note', align='right'),

    ], style={'padding':'5px'}, class_name='filter_panel'),
    
    dbc.Row([
        html.H2(id='wh_overall_title_tw'),
        html.H2(id='wh_overall_title_vn'),
    ], style={'padding-top':'10px'}),

    dbc.Row([
        html.Img(id='wh_overall_bar')
    ]),

])



@callback(
    [Output('wh_overall_bar', 'src'),
     Output('wh_overall_title_tw','children'),
     Output('wh_overall_title_vn','children'),
    ],
    
    [Input('wh_overall_day_slicer','value'),
     Input('wh_overall_target_month','value'),
     Input('wh_overall_target_year','value')]
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