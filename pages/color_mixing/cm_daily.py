# # -*- coding: utf-8 -*-
# """
# Created on Mon Sep 23 11:03:46 2024

# @author: KT1
# """

# import dash
# from dash import html, dcc, dash_table, callback, Input, Output
# import dash_bootstrap_components as dbc
# import plotly.express as px
# import pandas as pd

# dash.register_page(__name__, path="/cm_daily")

# df = pd.read_excel(r"data\color_mixing.xlsx")


# layout = dbc.Container([
#     dbc.Row([
#         dbc.Col([
#             html.H1('Color-Mixing Daily Report')
#         ], width=12),

#         dbc.Col([
#             html.Title("Select Date Range"),
#             # Add DatePickerRange
#             dcc.DatePickerRange(
#             id='date-picker-range',
#             start_date_placeholder_text='Start date',
#             end_date_placeholder_text='End date'
#             )
#         ]),

#     ]),


#     dbc.Row([
#         dbc.Col([
#             html.H2("Loss rate by date"),
#             dcc.Graph(figure={}, id='line_loss_rate_date')
#         ], width=12)
#     ]),

#     dbc.Row([
#         dbc.Col([
#             html.Title("Loss rate"),
#             dcc.Graph(figure={}, id='bar_loss_rate_category')
#         ], width=6),

#         dbc.Col([
#             html.Title("Data selected from ERP"),
#             dash_table.DataTable(id='table_data_date', page_size=12),
#         ], width=6)
#     ]),

# ])

# @callback(
#     [Output(component_id='line_loss_rate_date', component_property='figure')],
#     [Input(component_id='date-picker-range', component_property='start_date'),
#      Input(component_id='date-picker-range', component_property='end_date')]
# )

# def update_content(start_date, end_date):
#     # Filter by selected date range
#     if start_date and end_date:
#         dff = df[(df['complete_date'] >= start_date) & (df['complete_date'] <= end_date)]
#     else:
#         dff = df.copy()
#     # Update the data for the table

#     # Line chart - loss rate
#     df_loss_rate = dff.groupby('complete_date').agg({'actual_quantity':'sum',
#                                           'loss_quantity':'sum'}
#                                           ).reset_index()
#     df_loss_rate['loss_rate'] = df_loss_rate['loss_quantity'] / df_loss_rate['actual_quantity'] * 100
#     df_loss_rate['loss_rate'] = df_loss_rate['loss_rate'].round(2)
#     fig_loss_rate_date = px.line(df_loss_rate, x='complete_date', y='loss_rate')
#     # Add average line
#     average_value = df_loss_rate['loss_quantity'].sum() / df_loss_rate['actual_quantity'].sum() * 100
#     fig_loss_rate_date.add_shape(
#     type="line",
#     x0=df_loss_rate['complete_date'].min(),  # Starting x position (min date)
#     x1=df_loss_rate['complete_date'].max(),  # Ending x position (max date)
#     y0=average_value,     # The y-value for the line (average)
#     y1=average_value,     # The y-value for the line (average)
#     line=dict(color="Red", width=2, dash="dash"),  # Customize the line style
# )

#     return [fig_loss_rate_date]

# @callback(
#     [Output('bar_loss_rate_category', 'figure'),
#      Output('table_data_date','data')],
#     Input('line_loss_rate_date', 'hoverData')
# )
# def update_bar(hoverData):
#     if hoverData is None:
#         fig = px.histogram(df, x='category', histfunc='sum')
#         dff = df[['product_name','actual_quantity','loss_quantity','loss_rate']]
#         dff['loss_rate'] = round(dff['loss_rate'] * 100,2)
#         return fig, dff.to_dict('records')

#     # Extract the date from hoverData
#     hover_date = hoverData['points'][0]['x']  # Assuming x contains the date
#     dff = df[df['complete_date'] == hover_date]

#     dff_category = dff.groupby('category', as_index=False).agg({'estimated_quantity':'sum'})
#     dff_category.columns = ['category','estimated_quantity']
#     fig = px.bar(dff_category, x='category',y='estimated_quantity')
#     dff['loss_rate'] = round(dff['loss_rate'] * 100,2)
#     return fig, dff[['product_name','actual_quantity','loss_quantity','loss_rate']].to_dict('records')
