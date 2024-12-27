import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import os
import base64
import io
from datetime import datetime, timedelta
import pandas as pd
import constants
from extract import get_all_row_order, get_all_row_sales

dash.register_page(__name__, path="/wh_data")

today = datetime.today().date()
yesterday = today - timedelta(days=1)
first_date = today.replace(day=1)

def process_upload_data(contents, filename, last_modified, folder_path):
    # Decode the file content
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    if '.xls' in filename:
        # Save the file to the upload folder
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "wb") as f:
            f.write(decoded)

        return dbc.Alert(
                f"File '{filename}' tải lên thành công!",
                color="success",
            )
    else:
        return dbc.Alert(
            f"Lỗi khi đọc '{filename}'. Dữ liệu không hợp lệ.",
            color="danger",
        )

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            #Order
            html.H1("Tải dữ liệu ĐĐH lên", className="text-center my-4"),
            dcc.Upload(
                id="wh_data_upload_order",
                children=html.Div(["Kéo thả ĐĐH vào đây hoặc ", html.A("Chọn File",style={"fontWeight": "bold"})]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                multiple=False,  # Allow only one file at a time
            ),
            html.Div(id="wh_data_upload_order_status", className="mt-3"),
        ]),

        dbc.Col([
            #Sales
            html.H1("Tải dữ liệu Giao hàng lên", className="text-center my-4"),
            dcc.Upload(
                id="wh_data_upload_sales",
                children=html.Div(["Kéo thả GH vào đây hoặc ", html.A("Chọn File",style={"fontWeight": "bold"})]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                multiple=False,  # Allow only one file at a time
            ),
            html.Div(id="wh_data_upload_sales_status", className="mt-3"),
        ]),
    ],class_name='filter_panel', style={'padding':'5px'}),

    
    dbc.Row([
        dbc.Col(html.H1("Tải dữ liệu về", className="text-center my-4")),
        dbc.Col([
            html.H6(["選擇日期範圍", html.Br(), "Chọn khoảng thời gian"]),
            # Add DatePickerRange
            dcc.DatePickerRange(
            id='wh_data_date_range',
            start_date=first_date,
            end_date=yesterday,
            updatemode='bothdates',
            display_format=constants.date_format,
            )
        ]),
    ]),

    dbc.Button(id='wh_data_download_order', children="Tải dữ liệu ĐĐH", color="primary", className="me-1"),
    dcc.Download(id="wh_data_download_btn_order"),
    dash_table.DataTable(id='wh_data_table_order',
                         filter_action="native",
                         sort_action="native",
                         style_table={'height': '300px', 'overflowY': 'auto'}),
    
    dbc.Button(id='wh_data_download_sales', children="Tải dữ liệu GH", color="success", className="me-1"),
    dcc.Download(id="wh_data_download_btn_sales"),
    dash_table.DataTable(id='wh_data_table_sales',
                         filter_action="native",
                         sort_action="native",
                         style_table={'height': '300px', 'overflowY': 'auto'}),
    

])

#Upload order data
@callback(
    Output("wh_data_upload_order_status", "children"),
    Input("wh_data_upload_order", "contents"),
    State("wh_data_upload_order", "filename"),
    State("wh_data_upload_order", "last_modified"),
)
def save_uploaded_order(contents, filename, last_modified):
    if contents is not None:
        return process_upload_data(contents, filename, last_modified, constants.wh_data_folder_order)

    return dbc.Alert("Chưa có file được tải lên", color="info")

#Upload sales data
@callback(
    Output("wh_data_upload_sales_status", "children"),
    Input("wh_data_upload_sales", "contents"),
    State("wh_data_upload_sales", "filename"),
    State("wh_data_upload_sales", "last_modified"),
)
def save_uploaded_order(contents, filename, last_modified):
    if contents is not None:
        return process_upload_data(contents, filename, last_modified, constants.wh_data_folder_sales)

    return dbc.Alert("Chưa có file được tải lên", color="info")


#Show order and sales table
@callback(
    [Output('wh_data_table_order','data'),
     Output('wh_data_table_order','columns'),
     Output('wh_data_table_sales','data'),
     Output('wh_data_table_sales','columns')],

    [Input('wh_data_date_range','start_date'),
     Input('wh_data_date_range','end_date')],
     prevent_initial_call=True,
)

def load_data(start_date, end_date):
    df_order = get_all_row_order(start_date, end_date)
    df_order.columns = ['Ngày ĐĐH','Mã ĐĐH','Ngày CT','Mã KH','Mã ĐĐH của KH',
                        'Loại thuế','Bộ phận','NVBH','Tỉ lệ trả trước','Mã đăng ký thanh toán',
                        'Tên đăng ký thanh toán','địa chỉ GH','Mã SP','Tên SP','QC','Loại kho',
                        'SL ĐĐH','SL ĐĐH đã giao','SL đóng gói ĐĐH','SL đóng gói ĐĐH đã giao',
                        'Đơn vị','Đơn vị đóng gói','Thời gian dự định GH','Thời gian dự định GH ban đầu',
                        'CT trước','Mã kết thúc','import_timestamp','import_wh_timestamp','Mã KH 2','Tên KH']
    df_order.drop(columns=['Mã KH 2'], inplace=True)
    df_order_columns=[{"name": i, 'id': i} for i in df_order.columns]

    df_sales = get_all_row_sales(start_date, end_date)
    df_sales.columns = ['Mã SP','Tên SP','QC','Mã KH','Ngày GH','Mã GH',
                        'Mã ĐĐH','SL GH','Đơn vị','SL đóng gói','Đơn vị đóng gói',
                        'Bộ phận','NVBH','Mã kho','Loại kho','Mã nhập kho','Mã ĐĐH của KH',
                        'import_timestamp','import_wh_timestamp','Mã KH 2','Tên KH']
    df_sales.drop(columns=['Mã KH 2'], inplace=True)
    df_sales_columns=[{"name": i, 'id': i} for i in df_sales.columns]

    return [df_order.to_dict('records'), df_order_columns,
            df_sales.to_dict('records'), df_sales_columns]

#Download order data
@callback(
    Output('wh_data_download_btn_order', 'data'),
    Input('wh_data_download_order', 'n_clicks'),
    [State('wh_data_table_order', 'data'),
     State('wh_data_table_order', 'columns')],
     prevent_initial_call=True,
)
def download_order_data(n_clicks, table_data, table_columns):
    if n_clicks:
        df_order = pd.DataFrame(table_data, columns=[col['name'] for col in table_columns])
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_order.to_excel(writer, index=False, sheet_name='OrderData')
        output.seek(0)
        return dcc.send_bytes(output.getvalue(), "ĐĐH.xlsx")

#Download sales data
@callback(
    Output('wh_data_download_btn_sales', 'data'),
    Input('wh_data_download_sales', 'n_clicks'),
    [State('wh_data_table_sales', 'data'),
     State('wh_data_table_sales', 'columns'),],
     prevent_initial_call=True,
)
def download_sales_data(n_clicks, table_data, table_columns):
    if n_clicks:
        df_sales = pd.DataFrame(table_data, columns=[col['name'] for col in table_columns])
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_sales.to_excel(writer, index=False, sheet_name='SalesData')
        output.seek(0)
        return dcc.send_bytes(output.getvalue(), "GH.xlsx")