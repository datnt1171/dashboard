import dash
from dash import html, callback, Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np

dash.register_page(__name__, path="/s_systemsheet")



# Initial table structure (empty or with placeholder rows/columns)
columns = ['Column 1', 'Column 2', 'Column 3', 'Column 4']
data = [{'Column 1': '', 'Column 2': '', 'Column 3': '', 'Column 4': ''} for _ in range(5)]  # 5 empty rows

layout = dbc.Container([
    dbc.Col([
        html.H3("Paste Your Data Below:"),
        dash_table.DataTable(
            id='editable-table',
            columns=[{'name': col, 'id': col, 'editable': True} for col in columns],
            data=data,
            editable=True,  # Allow user to edit cells
            row_deletable=True,  # Allow users to delete rows
            style_table={'overflowX': 'auto'},  # Add horizontal scrolling if needed
        ),
        html.Button("Add Row", id="add-row-btn", n_clicks=0),
        html.Div(id="output-div"),  # Output div to display the table's data for debugging
    ], width=3),

    dbc.Col([
        html.H3("Paste Your Data Below:"),
        dash_table.DataTable(
            id='editable-table',
            columns=[{'name': col, 'id': col, 'editable': True} for col in columns],
            data=data,
            editable=True,  # Allow user to edit cells
            row_deletable=True,  # Allow users to delete rows
            style_table={'overflowX': 'auto'},  # Add horizontal scrolling if needed
        ),
        html.Button("Add Row", id="add-row-btn", n_clicks=0),
        html.Div(id="output-div"),  # Output div to display the table's data for debugging
    ], width=3)
])

@callback(
    Output('editable-table', 'data'),
    Input('add-row-btn', 'n_clicks'),
    State('editable-table', 'data'),
    State('editable-table', 'columns')
)
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        # Append an empty row to the table
        rows.append({col['id']: '' for col in columns})
    return rows

@callback(
    Output("output-div", "children"),
    Input("editable-table", "data")
)
def display_data(data):
    # Display the current data from the table (for debugging)
    return f"Table Data: {data}"

