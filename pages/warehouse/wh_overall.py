import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc


from utils.query.wh.extract import get_mtd_by_month, extract_order_target, extract_sales_target
from utils.plot_fig import plot_sales_order_target
from utils.query.wh.extract import get_max_sales_date
from utils import constants


dash.register_page(__name__, path="/wh_overall")

def layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    html.H6("選擇日期範圍 - Chọn khoảng thời gian"), #Select day range
                    # Add RangeSlider
                    dcc.RangeSlider(1, 31, 1,
                                    value=[1, get_max_sales_date().day], 
                                    id='wh_overall_day_slicer',
                                    marks={i: {'label': str(i), 'style': {'color': 'gray' if i > get_max_sales_date().day else 'black'}} for i in range(1, 32)},),
                ]),
            ], width=5),

            dbc.Col([
                html.H6("目標月份"), #Target month
                dcc.Dropdown(options=constants.LIST_MONTH, # Month Option
                            value=5,
                            id='wh_overall_target_month',
                            clearable=False),
            ], width=1),

            dbc.Col([
                html.H6("目標年"), #Target Year 
                dcc.Dropdown(options=constants.LIST_YEAR, # Year Option
                            value=2022,
                            id='wh_overall_target_year',
                            clearable=False)
            ], width=1),

            dbc.Col([
                html.H6("今年 - Năm hiện tại"), #Target Year 
                dcc.Dropdown(options=constants.LIST_YEAR, # Year Option
                            value=2025,
                            id='wh_overall_selected_year',
                            clearable=False)
            ], width=2),

            dbc.Col([
                dbc.Row([
                    html.H6(f'更新資料到達 - Dữ liệu cập nhật đến ngày: {get_max_sales_date()}')
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
     Input('wh_overall_target_year','value'),
     Input('wh_overall_selected_year','value')]
)

def update_bar_sales(day_range, target_month, target_year, selected_year):
    # Get data
    ## order_all
    df_order = get_mtd_by_month(selected_year, 
                                day_range[0], 
                                day_range[1], 
                                constants.EXCLUDE_FACTORY, 
                                "fact_order", 
                                "order_quantity", 
                                "order_date")
    df_order.columns = ['month','order_quantity','order_quantity_timber']
    ## sales_all
    df_sales = get_mtd_by_month(selected_year, 
                                day_range[0], 
                                day_range[1], 
                                constants.EXCLUDE_FACTORY, 
                                "fact_sales", 
                                "sales_quantity", 
                                "sales_date")
    df_sales.columns = ['month','sales_quantity','sales_quantity_timber']
    ## order target
    order_target = extract_order_target(day_range, target_month, target_year)

    ## sales target
    sales_target = extract_sales_target(day_range, target_month, target_year)

    # Merge for plotting
    df = df_order.merge(df_sales, on='month', how='outer')
    df.fillna(0, inplace=True)
    df['sales_target%'] = df['sales_quantity'] / sales_target
    df['order_target%'] = df['order_quantity'] / order_target
    fig_bar_matplotlib = plot_sales_order_target(df, target_year, target_month)
    title_tw = f"2024年每月送貨比较与{target_year}年{target_month}月相比 （每月{day_range[0]}日~{day_range[1]}日）"
    title_vn = f"SO SÁNH SỐ LƯỢNG GIAO HÀNG MỖI THÁNG SO VỚI THÁNG {target_month} NĂM {target_year}"
    return [fig_bar_matplotlib, title_tw, title_vn]