# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 11:03:46 2024

@author: KT1
"""

import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

dash.register_page(__name__ ,path="/cm_weekly")

df = pd.read_excel(r"data\color_mixing.xlsx")


layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('Color-Mixing Weekly Report')
        ], width=12)
    ], justify="center"),
    
    dbc.Row([
        dbc.Col([
            html.H2("Select Date Range"),
            # Add DatePickerRange
            dcc.DatePickerRange(
            id='date-picker-range',
            start_date_placeholder_text='Start date',
            end_date_placeholder_text='End date'
            )
        ]),

        dbc.Col([
            html.Title("Select Group Level"),
            dbc.RadioItems(
                    id="radios_paint_type",
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active",
                    options=[
                        {"label": "Paint System", "value": "paint_type"},
                        {"label": "Category", "value": "category"},
                        {"label": "Sub Category", "value": "sub_category_1"},
                        {"label": "Sub Category 2", "value": "sub_category_2"}
                        
                    ],
                    value="paint_type",
                )
            ])
    ]),

    dbc.Row([
        dbc.Col([
            html.H2("木漆~烤漆一周生產量 (Kg)", className="text-center"),
            dcc.Graph(figure={}, id='bar_actual_quantity_week')
        ], width={"size": 6, "offset": 3}),

        dbc.Col([
            html.H2("木漆~烤漆一周生產批數 (批數)", className="text-center"),
            dcc.Graph(figure={}, id='bar_production_batch_week')
        ], width={"size": 6, "offset": 3})
    ]),

    dbc.Row([
        dbc.Col([
            html.H2("木漆~烤漆一周损耗率 (%)", className="text-center"),
            dcc.Graph(figure={}, id='bar_loss_rate_week')
        ], width={"size": 6, "offset": 3})
    ]),

    # dbc.Row([
    #     dbc.Col([
    #         html.H2("Data selected from ERP"),
    #         dash_table.DataTable(id='table_data_week', page_size=6),
    #     ], width=12)
    # ])

])

@callback(
    [Output(component_id='bar_actual_quantity_week', component_property='figure'),
     Output(component_id='bar_production_batch_week', component_property='figure'),
     Output(component_id='bar_loss_rate_week', component_property='figure'),],
    [Input(component_id='date-picker-range', component_property='start_date'),
     Input(component_id='date-picker-range', component_property='end_date'),
     Input('radios_paint_type', 'value')]
)

def update_content(start_date, end_date, radios_value):
    # Filter by selected date range
    if start_date and end_date:
        dff = df[(df['complete_date'] >= start_date) & (df['complete_date'] <= end_date)]
    else:
        dff = df.copy()

    # Create bar chart for actual quantity
    dff_actual = dff.groupby(radios_value).agg({'estimated_quantity':'sum'}).reset_index()
    dff_actual.sort_values(radios_value, inplace=True)
    dff_actual['estimated_quantity'] = dff_actual['estimated_quantity'].round(0)
    fig_actual = px.bar(
        dff_actual,
        x=radios_value,
        y='estimated_quantity',
        color=radios_value,
        color_discrete_map={
            "SG": "yellow",  # Map "SG" to yellow
            "SH": "green",
            "Silver": "gray"   # Map "SH" to green
        }, text_auto=True,
        height=600
    )

    fig_actual.update_traces(textposition='outside', textfont_size=14, textangle=0)
    fig_actual.update_layout(
        xaxis_title="油漆類型",
        yaxis_title="數量",
        yaxis=dict(
            tickformat=',.0f'  # This removes the comma from the numbers
            ),
        title={
            'text': f"{start_date} 到 {end_date}",
            'x': 0.5,  # Position it in the center
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    # Create bar chart for number of batch
    dff_num_batch = dff.groupby(radios_value).agg({'estimated_quantity':'count'}).reset_index()
    dff_num_batch.sort_values(radios_value,inplace=True)
    dff_num_batch.columns = [radios_value,'number_of_batch']
    fig_num_batch = px.bar(
    dff_num_batch,
    x=radios_value,
    y='number_of_batch',
    color=radios_value,
    color_discrete_map={
        "SG": "yellow",  # Map "SG" to yellow
        "SH": "green",
        "Silver": "gray"    # Map "SH" to green
    }, text_auto=True,
    height=600
)
    fig_num_batch.update_traces(textposition='outside', textfont_size=14, textangle=0)
    fig_num_batch.update_layout(
    xaxis_title="油漆類型",
    yaxis_title="批數",
    title={
        'text': f"{start_date} 到 {end_date}",
        'x': 0.5,  # Position it in the center
        'xanchor': 'center',
        'yanchor': 'top'
    }
)

    # Create bar chart for Loss rate
    dff_loss = dff.groupby(radios_value).agg({'actual_quantity':'sum',
                                              'loss_quantity':'sum'}
                                             ).reset_index()
    dff_loss['loss_rate'] = dff_loss['loss_quantity'] / dff_loss['actual_quantity'] * 100
    dff_loss['loss_rate'] = dff_loss['loss_rate'].round(2)
    dff_loss.sort_values(radios_value,inplace=True)
    fig_loss_rate = px.bar(
    dff_loss,
    x=radios_value,
    y='loss_rate',
    color=radios_value,
    color_discrete_map={
        "SG": "yellow",  # Map "SG" to yellow
        "SH": "green",      # Map "SH" to green
        "Silver": "gray"    # Map "Silver" to gray
    }, text_auto=True,
    height=600
)
    fig_loss_rate.update_traces(textposition='outside', textfont_size=14, textangle=0)
    fig_loss_rate.update_layout(
    xaxis_title="油漆類型",
    yaxis_title="損耗率",
    title={
        'text': f"{start_date} 到 {end_date}",
        'x': 0.5,  # Position it in the center
        'xanchor': 'center',
        'yanchor': 'top'
    }
)

    return fig_actual, fig_num_batch, fig_loss_rate