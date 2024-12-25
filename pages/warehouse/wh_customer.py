import dash
from dash import html, dcc, dash_table, callback, Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta, date
import calendar
from dateutil.relativedelta import relativedelta

from extract import get_mtd_factory_sales, get_mtd_factory_order, \
get_planned_deliveries, get_total_sales, get_total_order
from extract import get_max_sales_date
import constants


dash.register_page(__name__, path="/wh_customer")




today = datetime.today().date()
yesterday = today - timedelta(days=1)
first_date = today.replace(day=1)

same_day_last_month = yesterday - relativedelta(months=1)
same_day_last_month_fisrt = same_day_last_month.replace(day=1)

def layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.RadioItems(
                    id="wh_customer_radios_sales",
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active",
                    options=[
                        {"label": "送货 GIAO HÀNG", "value": "sales"},
                        {"label": "訂單 ĐĐH", "value": "order"},
                    ],
                    value="sales",
                ),

                dbc.RadioItems(
                    id="wh_customer_radios_sort",
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active",
                    options=[
                        {"label": "增加↑↑ Tăng↑↑", "value": "increase"},
                        {"label": "減少↓↓ Giảm↓↓", "value": "decrease"},
                    ],
                    value="increase",
                ),

            ]),

            dbc.Col([
                html.H6(["選擇要比較的時間段", html.Br(),"Chọn khoảng thời gian để so sánh"]),
                # Add DatePickerRange for target
                dcc.DatePickerRange(
                id='wh_customer_date_range_target',
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
                id='wh_customer_date_range',
                start_date=first_date,
                end_date=yesterday,
                updatemode='bothdates',
                display_format=constants.date_format,
                
                )
            ]),

            dbc.Col([
                html.H6(["负责人", html.Br(), "Tiếp thị đảm nhiệm"]),
                dcc.Dropdown(id='wh_customer_dropdown_salesman',
                            options=constants.SALESMAN + ['全部 - Tất cả'],
                            value='全部 - Tất cả',
                            clearable=False,
                            )
            ], width=2),

            dbc.Col([
                dbc.Row([
                    html.H6(f'更新資料到達 - Dữ liệu cập nhật đến ngày: {get_max_sales_date()}')
                ]),
                # dbc.Row([
                #     html.H6(f'更新於 - Cập nhật vào lúc: {max_import_wh_timestamp.date()}')
                # ])
            ], width=2, class_name='update_note'),

        ],class_name='filter_panel', style={'padding':'5px'}),

    ####################################################################################
        dbc.Row([
            dbc.Col([
                html.H2(id='wh_customer_title_sales_increase'),
                dash_table.DataTable(
                    id='wh_customer_table_sales_increase',
                    #sort_action="native",
                    style_cell_conditional=[
                        {
                            'if': {'column_id': ['數字順序 - STT', '客戶代號 MÃ KHÁCH HÀNG','客戶名称 TÊN KHÁCH HÀNG']},
                            'textAlign': 'left'
                        },
                        {
                            'if': {
                                'column_id': '数量差异 SỐ LƯỢNG CHÊNH LỆCH',
                            },
                            'backgroundColor': '#FFFF00',
                        },
                    ],
                    style_cell={
                        'padding': '5px',
                        'minWidth': '80px', 'maxWidth': '120px', 'whiteSpace': 'normal'  # Control column width
                    },
                    
                    # Style the table header
                    style_header={
                        'backgroundColor': '#C1FFC1',
                        'fontWeight': 'bold',
                        'font-color': 'white'
                    },
                    
                    # Remove or adjust spacing if needed
                    style_data={
                        'whiteSpace': 'normal',  # Wrap text instead of adding extra space
                        'height': 'auto',        # Allow the row height to adjust
                        'lineHeight': '15px'     # Control line spacing
                    },

                ),
                
            ], width=12)
        ],style={'margin-top': '10px',"display": "block"},id='wh_customer_row_sales_increase'),


        dbc.Row([
            dbc.Col([
                html.H2(id='wh_customer_title_sales_decrease'),
                dash_table.DataTable(
                    id='wh_customer_table_sales_decrease',
                    #sort_action="native",
                    style_cell_conditional=[
                        {
                            'if': {'column_id': ['數字順序 - STT', '客戶代號 MÃ KHÁCH HÀNG','客戶名称 TÊN KHÁCH HÀNG']},
                            'textAlign': 'left'
                        },
                        {
                            'if': {
                                'column_id': '数量差异 SỐ LƯỢNG CHÊNH LỆCH',
                            },
                            'backgroundColor': '#FFFF00',
                        },
                    ],
                    style_cell={
                        'padding': '5px',
                        'minWidth': '80px', 'maxWidth': '120px', 'whiteSpace': 'normal'  # Control column width
                    },
                    
                    # Style the table header
                    style_header={
                        'backgroundColor': '#C1FFC1',
                        'fontWeight': 'bold',
                        'font-color': 'white'
                    },
                    
                    # Remove or adjust spacing if needed
                    style_data={
                        'whiteSpace': 'normal',  # Wrap text instead of adding extra space
                        'height': 'auto',        # Allow the row height to adjust
                        'lineHeight': '15px'     # Control line spacing
                    },

                ),
                
            ], width=12)
        ],style={'margin-top': '10px',"display": "block"},id='wh_customer_row_sales_decrease'),





        dbc.Row([
            dbc.Col([
                html.H2(id='wh_customer_title_order_increase'),
                dash_table.DataTable(
                    id='wh_customer_table_order_increase',
                    #sort_action="native",
                    style_cell_conditional=[
                        {
                            'if': {'column_id': ['數字順序 - STT', '客戶代號 MÃ KHÁCH HÀNG','客戶名称 TÊN KHÁCH HÀNG']},
                            'textAlign': 'left'
                        },
                        {
                            'if': {
                                'column_id': '数量差异 SỐ LƯỢNG CHÊNH LỆCH',
                            },
                            'backgroundColor': '#FFFF00',
                        },
                    ],
                    style_cell={
                        'padding': '5px',
                        'minWidth': '80px', 'maxWidth': '120px', 'whiteSpace': 'normal'  # Control column width
                    },
                    
                    # Style the table header
                    style_header={
                        'backgroundColor': '#DFF2EB',
                        'fontWeight': 'bold'
                    },
                    
                    # Remove or adjust spacing if needed
                    style_data={
                        'whiteSpace': 'normal',  # Wrap text instead of adding extra space
                        'height': 'auto',        # Allow the row height to adjust
                        'lineHeight': '15px'     # Control line spacing
                    },

                ),
                
            ], width=12)

        ],style={'margin-top': '10px',"display": "none"},id='wh_customer_row_order_increase'),


        dbc.Row([
            dbc.Col([
                html.H2(id='wh_customer_title_order_decrease'),
                dash_table.DataTable(
                    id='wh_customer_table_order_decrease',
                    #sort_action="native",
                    style_cell_conditional=[
                        {
                            'if': {'column_id': ['數字順序 - STT', '客戶代號 MÃ KHÁCH HÀNG','客戶名称 TÊN KHÁCH HÀNG']},
                            'textAlign': 'left'
                        },
                        {
                            'if': {
                                'column_id': '数量差异 SỐ LƯỢNG CHÊNH LỆCH',
                            },
                            'backgroundColor': '#FFFF00',
                        },
                    ],
                    style_cell={
                        'padding': '5px',
                        'minWidth': '80px', 'maxWidth': '120px', 'whiteSpace': 'normal'  # Control column width
                    },
                    
                    # Style the table header
                    style_header={
                        'backgroundColor': '#DFF2EB',
                        'fontWeight': 'bold'
                    },
                    
                    # Remove or adjust spacing if needed
                    style_data={
                        'whiteSpace': 'normal',  # Wrap text instead of adding extra space
                        'height': 'auto',        # Allow the row height to adjust
                        'lineHeight': '15px'     # Control line spacing
                    },

                ),
                
            ], width=12)

        ],style={'margin-top': '10px',"display": "none"},id='wh_customer_row_order_decrease')

    ], fluid=True)

@callback(
        
    [Output('wh_customer_title_sales_increase', 'children'), #Title
     Output('wh_customer_table_sales_increase', 'data'),
     Output('wh_customer_table_sales_increase', 'columns'),
     Output('wh_customer_table_sales_increase', 'style_data_conditional'),
     
     Output('wh_customer_title_sales_decrease', 'children'), #Title
     Output('wh_customer_table_sales_decrease', 'data'),
     Output('wh_customer_table_sales_decrease', 'columns'),
     Output('wh_customer_table_sales_decrease', 'style_data_conditional'),],

    [Input('wh_customer_date_range', 'start_date'),
     Input('wh_customer_date_range', 'end_date'),
     Input('wh_customer_date_range_target', 'start_date'),
     Input('wh_customer_date_range_target', 'end_date'),
     Input('wh_customer_dropdown_salesman','value')]
)

def update_table_sales(start_date, end_date, start_date_target, end_date_target, salesman):

    # Convert to datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    start_date_target = datetime.strptime(start_date_target, '%Y-%m-%d')
    end_date_target = datetime.strptime(end_date_target, '%Y-%m-%d')
        

    df = get_mtd_factory_sales(start_date, end_date, start_date_target, end_date_target)

    df[['total_quantity','total_quantity_prev','quantity_diff']] = \
    df[['total_quantity','total_quantity_prev','quantity_diff']].round(0)

    df['pct_change'] = df['pct_change'].round(2)
    df['pct_change'] = df['pct_change'].map("{:,.2f}%".format)

    df.sort_values(by='quantity_diff', ascending=True, inplace=True)

    # Append other information
    # factory_list = df['factory_code']
    total_sales = get_total_sales(df['factory_code'], start_date_target.year, start_date_target.month)
    df = df.merge(total_sales, how='left', on='factory_code')

    ### CHECK THIS AGAIN ###
    df.drop_duplicates(subset=['factory_code'], inplace=True) 
    ### CHECK THIS AGAIN ###

    last_day = calendar.monthrange(end_date.year, end_date.month)[1]
    last_date =  date(end_date.year, end_date.month, last_day)
    end_date_plus_1_day = end_date + relativedelta(days=1)

    if last_date == end_date:
        df['planned_deliveries'] = 0
    else:
        df_planned_deliveries = get_planned_deliveries(end_date_plus_1_day, last_date, df['factory_code'])
        df = df.merge(df_planned_deliveries, how='left', on='factory_code')

    df['index'] = df.index + 1
    if salesman != '全部 - Tất cả':
        df = df[df['salesman']==salesman]

    df = df[["index",'factory_code','factory_name','sales_prev','total_quantity_prev',
                     'total_quantity','quantity_diff','pct_change','planned_deliveries']]
    df.fillna(0,inplace=True)
    
    new_column_names = {
        'index': '數字順序 - STT',
        'factory_code': '客戶代號 MÃ KHÁCH HÀNG',
        'factory_name': '客戶名称 TÊN KHÁCH HÀNG',
        #'salesman': '负责人',
        'sales_prev': f'整個月的送货數量 SỐ LƯỢNG GIAO HÀNG CẢ THÁNG {start_date_target.month}',
        'total_quantity': f'{start_date.year}-{start_date.month}-{start_date.day}~{end_date.year}-{end_date.month}-{end_date.day} 送货数量 SỐ LƯỢNG GIAO HÀNG',
        'total_quantity_prev': f'{start_date_target.year}-{start_date_target.month}-{start_date_target.day} \
        ~{end_date_target.year}-{end_date_target.month}-{end_date_target.day} 送货数量 SỐ LƯỢNG GIAO HÀNG',
        'quantity_diff': '数量差异 SỐ LƯỢNG CHÊNH LỆCH',
        'pct_change': '% 差異 TỈ LỆ CHÊNH LỆCH',
        'planned_deliveries': f'訂單未交數量 SỐ LƯỢNG ĐĐH CHƯA GIAO'
    }
    df = df.rename(columns=new_column_names)


    columns = [{"name": i, "id": i} for i in df.columns]

    # Apply conditional styling to highlight cells with value 0
    style_data_conditional = [
        {
            'if': {
                'filter_query': '{{{col}}} = 0'.format(col=col),  # Target individual cell value
                'column_id': col  # Apply only to the column (cell-level)
            },
            'backgroundColor': '#F9AD95',
        }
        for col in df.columns[0:-1] # Apply the rule to all columns EXCEPT LAST COLUMN
    ]

    title_increase = [f"{start_date.year}年{end_date.month}月比{start_date_target.year} \
    年{start_date_target.month}月分客戶送加与的名单(1000KG 以上)", html.Br(), 
    f"Giao hàng tháng {end_date.month}, {start_date.year} tăng so với {start_date_target.month}, {start_date_target.year}"]

    title_decrease = [f"{start_date.year}年{end_date.month}月比{start_date_target.year} \
    年{start_date_target.month}月分客戶送少与的名单(1000KG 以上)", html.Br(),
    f"Giao hàng tháng {end_date.month}, {start_date.year} giảm so với {start_date_target.month}, {start_date_target.year}"]


    df_increase = df[df['数量差异 SỐ LƯỢNG CHÊNH LỆCH']>=1000]
    df_decrease = df[df['数量差异 SỐ LƯỢNG CHÊNH LỆCH']<=-1000]
    df_increase.sort_values(by='数量差异 SỐ LƯỢNG CHÊNH LỆCH', ascending=False, inplace=True)
    df_decrease.sort_values(by='数量差异 SỐ LƯỢNG CHÊNH LỆCH', ascending=True, inplace=True)

    df_increase.reset_index(inplace=True, drop=True)
    df_increase['數字順序 - STT'] = df_increase.index + 1

    df_decrease.reset_index(inplace=True, drop=True)
    df_decrease['數字順序 - STT'] = df_decrease.index + 1


    numeric_col_index = [3,4,5,6,8]
    for col in numeric_col_index:
        df_increase.iloc[:,col] = df_increase.iloc[:,col].map("{:,.0f}".format)
        df_decrease.iloc[:,col] = df_decrease.iloc[:,col].map("{:,.0f}".format)


    return [title_increase, df_increase.to_dict('records'), columns, style_data_conditional,
            title_decrease, df_decrease.to_dict('records'), columns, style_data_conditional,]






@callback(
        
    [Output('wh_customer_title_order_increase', 'children'), #Title
     Output('wh_customer_table_order_increase', 'data'),
     Output('wh_customer_table_order_increase', 'columns'),
     Output('wh_customer_table_order_increase', 'style_data_conditional'),
    
     Output('wh_customer_title_order_decrease', 'children'), #Title
     Output('wh_customer_table_order_decrease', 'data'),
     Output('wh_customer_table_order_decrease', 'columns'),
     Output('wh_customer_table_order_decrease', 'style_data_conditional'),],

    [Input('wh_customer_date_range', 'start_date'),
     Input('wh_customer_date_range', 'end_date'),
     Input('wh_customer_date_range_target', 'start_date'),
     Input('wh_customer_date_range_target', 'end_date'),
     Input('wh_customer_dropdown_salesman','value')]
)

def update_table_order(start_date, end_date, start_date_target, end_date_target, salesman):

    # Convert to datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    start_date_target = datetime.strptime(start_date_target, '%Y-%m-%d')
    end_date_target = datetime.strptime(end_date_target, '%Y-%m-%d')

    df = get_mtd_factory_order(start_date, end_date, start_date_target, end_date_target)

    df[['total_quantity','total_quantity_prev','quantity_diff']] = \
    df[['total_quantity','total_quantity_prev','quantity_diff']].round(0)

    df['pct_change'] = df['pct_change'].round(2)
    df['pct_change'] = df['pct_change'].map("{:,.2f}%".format)

    df.sort_values(by='quantity_diff', ascending=True, inplace=True)

    # Append other information
    #factory_list = df['factory_code']

    total_order = get_total_order(df['factory_code'], start_date_target.year, end_date_target.month)
    df = df.merge(total_order, how='left', on='factory_code')

    ### CHECK THIS AGAIN ###
    df.drop_duplicates(subset=['factory_code'], inplace=True) 
    ### CHECK THIS AGAIN ###

    df['index'] = df.index + 1
    if salesman != '全部 - Tất cả':
        df = df[df['salesman']==salesman]

    df = df[['index','factory_code','factory_name','order_prev','total_quantity_prev',
                     'total_quantity','quantity_diff','pct_change']]
    df.fillna(0,inplace=True)
    # Change the column name dynamically
    new_column_names = {
        'index': '數字順序 - STT',
        'factory_code': '客戶代號 MÃ KHÁCH HÀNG',
        'factory_name': '客戶名称 TÊN KHÁCH HÀNG',
        #'salesman': '负责人',
        'order_prev': f'訂單總數 {start_date_target.year}年{end_date_target.month}月 - ĐĐH cả tháng {end_date_target.month}, {start_date_target.year}',
        'total_quantity': f'從日期{start_date.date()}到日期{end_date.date()}的訂單 - ĐĐH từ {start_date.date()} đến {end_date.date()}',
        'total_quantity_prev': f'從日期{start_date_target.date()}到日期{end_date_target.date()}的訂單 - ĐĐH từ {start_date_target.date()} đến {end_date_target.date()}',
        'quantity_diff': '数量差异 SỐ LƯỢNG CHÊNH LỆCH',
        'pct_change': '% 差異 TỈ LỆ CHÊNH LỆCH'
    }
    df = df.rename(columns=new_column_names)


    columns = [{"name": i, "id": i} for i in df.columns]

    # Apply conditional styling to highlight cells with value 0
    style_data_conditional = [
        {
            'if': {
                'filter_query': '{{{col}}} = 0'.format(col=col),  # Target individual cell value
                'column_id': col  # Apply only to the column (cell-level)
            },
            'backgroundColor': '#F9AD95',
        }
        for col in df.columns  # Apply the rule to all columns
    ]


    title_increase = f"{start_date.year}年{end_date.month}月比{start_date_target.year} \
    年{start_date_target.month}月分订单增加的名单(1000KG 以上)"

    title_decrease = f"{start_date.year}年{end_date.month}月比{start_date_target.year} \
    年{start_date_target.month}月分客戶订单减少的名单(1000KG 以上)"

    df_increase = df[df['数量差异 SỐ LƯỢNG CHÊNH LỆCH']>=1000]
    df_decrease = df[df['数量差异 SỐ LƯỢNG CHÊNH LỆCH']<=-1000]
    df_increase.sort_values(by='数量差异 SỐ LƯỢNG CHÊNH LỆCH',ascending=False, inplace=True)
    df_decrease.sort_values(by='数量差异 SỐ LƯỢNG CHÊNH LỆCH',ascending=True, inplace=True)

    df_increase.reset_index(inplace=True, drop=True)
    df_increase['數字順序 - STT'] = df_increase.index + 1

    df_decrease.reset_index(inplace=True, drop=True)
    df_decrease['數字順序 - STT'] = df_decrease.index + 1
    
    numeric_col_index = [3,4,5,6]
    for col in numeric_col_index:
        df_increase.iloc[:,col] = df_increase.iloc[:,col].map("{:,.0f}".format)
        df_decrease.iloc[:,col] = df_decrease.iloc[:,col].map("{:,.0f}".format)

    return [title_increase, df_increase.to_dict('records'), columns, style_data_conditional,
            title_decrease, df_decrease.to_dict('records'), columns, style_data_conditional,]


## Show/hide table
@callback(
    [Output('wh_customer_row_sales_increase','style'),
     Output('wh_customer_row_sales_decrease','style'),
     Output('wh_customer_row_order_increase','style'),
     Output('wh_customer_row_order_decrease','style')],
    [Input('wh_customer_radios_sales','value'),
     Input('wh_customer_radios_sort','value')]
)

def show_hide_table(radio_sales, radio_sort):
    if (radio_sales == 'sales') & (radio_sort == 'increase'):
        return [{'display':'block'}, {'display':'none'}, {'display':'none'}, {'display':'none'}]
    elif (radio_sales == 'sales') & (radio_sort == 'decrease'):
        return [{'display':'none'}, {'display':'block'}, {'display':'none'}, {'display':'none'}]
    elif (radio_sales == 'order') & (radio_sort == 'increase'):
        return [{'display':'none'}, {'display':'none'}, {'display':'block'}, {'display':'none'}]
    elif (radio_sales == 'order') & (radio_sort == 'decrease'):
        return [{'display':'none'}, {'display':'none'}, {'display':'none'}, {'display':'block'}]
    
        