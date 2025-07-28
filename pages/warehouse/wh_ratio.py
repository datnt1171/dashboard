import dash
from dash import html, dcc, dash_table, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from utils.query.wh.extract import get_sales_ratio
from utils.query.wh.extract import get_max_sales_date
from utils import constants


dash.register_page(__name__, path="/wh_ratio")

today = get_max_sales_date()

def layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([],width=3),
            dbc.Col([
                html.H2("按年份比較交貨 - So sánh tỉ lệ sản phẩm theo loại sơn"),
            ]),                     
            dbc.Col([
                dbc.Row([
                    html.H6(f'更新資料到達 - Dữ liệu cập nhật đến ngày: {get_max_sales_date()}')
                ]),
            ], width=2, class_name='update_note'),
        ], class_name='filter_panel'),
         
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    html.H6("今年 - Chọn Năm"), #Target Year
                     dcc.Dropdown(options=constants.LIST_YEAR, # Year Option
                            value=2025,
                            id='wh_ratio_selected_year',
                            clearable=False)
                    ], style= {'paddingBottom': '10px'}),
                                 
                dbc.Row([
                    html.H6("選擇油漆組 - Chọn nhóm sơn"),
                    dcc.Dropdown(id='wh_ratio_dropdown_paint',
                            options=['原料溶劑 NL DUNG MOI','樹脂NHUA CAY','粉類 BOT',
                                        '成品溶劑DUNG MOI TP','補土 BOT TRET',
                                        '半成品BAN THANHPHAM','硬化劑chat cung','色精TINH MAU',
                                        '水性SON NUOC','助劑PHU GIA','色母SON CAI',
                                        '木調色PM GO','烤調色PM HAP','底漆 LOT','面漆 BONG'],
                             value=['木調色PM GO','烤調色PM HAP','底漆 LOT','面漆 BONG'],
                            multi=True,
                            clearable=False,)
                ], style= {'paddingBottom': '10px'}),
                 
                dbc.Row([
                    html.H6("選擇年份 - Chọn dung môi"),
                    dcc.Dropdown(id='wh_ratio_dropdown_thinner',
                            options=['原料溶劑 NL DUNG MOI','樹脂NHUA CAY','粉類 BOT',
                                        '成品溶劑DUNG MOI TP','補土 BOT TRET',
                                        '半成品BAN THANHPHAM','硬化劑chat cung','色精TINH MAU',
                                        '水性SON NUOC','助劑PHU GIA','色母SON CAI',
                                        '木調色PM GO','烤調色PM HAP','底漆 LOT','面漆 BONG'],
                             value=['原料溶劑 NL DUNG MOI','成品溶劑DUNG MOI TP'],
                            multi=True,
                            clearable=False,)
                ], style= {'paddingBottom': '10px'}),
            ], id='wh_compare_sidebar', width=2),
            
            # Main content with three tables
            dbc.Col([
                # Ratio table
                dbc.Row([
                    html.H4("Tỉ lệ dung môi/sơn (比率)", style={'marginTop': '20px'}),
                    dash_table.DataTable(
                        id='wh_ratio_table_ratio',
                        export_format='xlsx',
                        export_headers='display',
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left', 'padding': '5px'},
                        style_header={'backgroundColor': 'lightyellow', 'fontWeight': 'bold'}
                    )
                ]),
                
                # Paint table
                dbc.Row([
                    html.H4("Giao hàng sơn (油漆組)", style={'marginTop': '20px'}),
                    dash_table.DataTable(
                        id='wh_ratio_table_paint',
                        export_format='xlsx',
                        export_headers='display',
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left', 'padding': '5px'},
                        style_header={'backgroundColor': 'lightblue', 'fontWeight': 'bold'}
                    )
                ], style={'marginBottom': '30px'}),
                
                # Thinner table  
                dbc.Row([
                    html.H4("Giao hàng dung môi (溶劑)", style={'marginTop': '20px'}),
                    dash_table.DataTable(
                        id='wh_ratio_table_thinner',
                        export_format='xlsx',
                        export_headers='display',
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left', 'padding': '5px'},
                        style_header={'backgroundColor': 'lightgreen', 'fontWeight': 'bold'}
                    )
                ], style={'marginBottom': '30px'}),
                
                
                             
            ], width=10),
          ]),
     ], fluid=True)

@callback(
    Output('wh_ratio_table_paint', 'data'),
    Output('wh_ratio_table_paint', 'columns'),
    Output('wh_ratio_table_thinner', 'data'),
    Output('wh_ratio_table_thinner', 'columns'),
    Output('wh_ratio_table_ratio', 'data'),
    Output('wh_ratio_table_ratio', 'columns'),
    [Input('wh_ratio_selected_year', 'value'),
     Input('wh_ratio_dropdown_paint', 'value'),
     Input('wh_ratio_dropdown_thinner', 'value')]
)
def update_ratio_tables(selected_year, selected_paint, selected_thinner):
    # Get data from database
    df = get_sales_ratio(selected_year)
    all_months = sorted(df['month'].unique())
    
    factories_months = df[['factory_code', 'factory_name', 'month']].drop_duplicates()
    df_thinner = (
    df[df['product_type'].isin(selected_thinner)]
    .groupby(['factory_code', 'factory_name', 'month'], as_index=False)['sales_quantity']
    .sum()
    )
    df_thinner = factories_months.merge(df_thinner, 
                                    on=['factory_code', 'factory_name', 'month'], 
                                    how='left').fillna({'sales_quantity': 0})
    
    df_paint = (
    df[df['product_type'].isin(selected_paint)]
    .groupby(['factory_code', 'factory_name', 'month'], as_index=False)['sales_quantity']
    .sum()
    )

    df_paint = factories_months.merge(df_paint, 
                                    on=['factory_code', 'factory_name', 'month'], 
                                    how='left').fillna({'sales_quantity': 0})
    
    thinner_df = df_thinner.pivot(index=['factory_code','factory_name'],
                              columns='month',
                              values='sales_quantity')
    
    paint_df = df_paint.pivot(index=['factory_code','factory_name'],
                              columns='month',
                              values='sales_quantity')
    ratio_df = thinner_df.div(paint_df.replace(0, np.nan)).fillna(0)
    
    # Reset index to be a df
    thinner_df.columns.name = None
    thinner_df.reset_index(inplace=True)
    
    paint_df.columns.name = None
    paint_df.reset_index(inplace=True)
    
    ratio_df.columns.name = None
    ratio_df.reset_index(inplace=True)

    factory_order = (
        df.groupby(['factory_code', 'factory_name'], as_index=False)['sales_quantity']
        .sum()
        .sort_values('sales_quantity', ascending=False)
        [['factory_code', 'factory_name']]
    )
    
    paint_df = paint_df.reset_index().merge(factory_order, on=['factory_code','factory_name'], how='right')
    thinner_df = thinner_df.reset_index().merge(factory_order, on=['factory_code','factory_name'], how='right')
    ratio_df = ratio_df.reset_index().merge(factory_order, on=['factory_code','factory_name'], how='right')


    # Create standardized columns for all tables
    columns = [
        {'name': 'Factory Code', 'id': 'factory_code'},
        {'name': 'Factory Name', 'id': 'factory_name'}
    ]
    
    ratio_columns = [
        {'name': 'Factory Code', 'id': 'factory_code'},
        {'name': 'Factory Name', 'id': 'factory_name'}
    ]
    
    for month in all_months:
        columns.append({
            'name': f'{month}月',
            'id': str(month),
            'type': 'numeric',
            'format': {'specifier': ',.0f'}
        })
        
        ratio_columns.append({
            'name': f'{month}月',
            'id': str(month),
            'type': 'numeric',
            'format': {'specifier': ',.2f'}
        })
    
    # Convert to dict for DataTable
    paint_data = paint_df.to_dict('records')
    thinner_data = thinner_df.to_dict('records')
    ratio_data = ratio_df.to_dict('records')
    
    return (paint_data, columns,
            thinner_data, columns,
            ratio_data, ratio_columns)
    


        