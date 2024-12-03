import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/rd_daily")

layout = dbc.Container([
    dbc.Row([
        html.H1('RD daily', style={'text-align':'center'})
    ])
])