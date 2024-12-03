import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/prod_weekly")

layout = dbc.Container([
    dbc.Row([
        html.H1('Production weekly', style={'text-align':'center'})
    ])
])