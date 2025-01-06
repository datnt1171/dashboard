import warnings
warnings.filterwarnings("ignore") 
import os
from db import Database
from dotenv import load_dotenv
load_dotenv()

# Dash
import dash
import dash_bootstrap_components as dbc
from dash import html, page_container, dcc, Input, Output

# Flask
from flask import Flask, request, redirect, session, jsonify, \
url_for, render_template
from flask_login import login_user, LoginManager, UserMixin, \
logout_user, current_user

# User
from user import get_users
df_user = get_users()
VALID_USERNAME_PASSWORD = df_user.set_index('username').to_dict(orient="index")
from utils.login_handler import disable_page

# Database
Database.initialize(
    database=os.getenv('WAREHOUSE_NAME'),
    user=os.getenv('WAREHOUSE_USER'),
    password=os.getenv('WAREHOUSE_PASSWORD'),
    host=os.getenv('WAREHOUSE_HOST'),
    port=os.getenv('WAREHOUSE_PORT'),
    minconn=1,
    maxconn=20
)
# Exposing the Flask Server so that it can be configured for the login process:
server = Flask(__name__)
# Updating the Flask Server configuration with a secret key to encrypt 
server.config.update(SECRET_KEY=os.getenv('SECRET_KEY'))

@server.before_request
def check_login():
    if request.method == 'GET':
        if request.path in ['/login', '/logout']:
            return
        if current_user:
            if current_user.is_authenticated:
                return
            else:
                for pg in dash.page_registry:
                    if request.path == dash.page_registry[pg]['path']:
                        session['url'] = request.url
        return redirect(url_for('login'))
    else:
        if current_user:
            if (request.path == '/login') or (current_user.is_authenticated):
                return
        return jsonify({'status':'401', 'statusText':'unauthorized access'})

@server.route('/login', methods=['POST', 'GET'])
def login(message=""):
    if request.method == 'POST':
        if request.form:
            username = request.form['username']
            password = request.form['password']
            if username not in VALID_USERNAME_PASSWORD or VALID_USERNAME_PASSWORD[username]['password'] != password:
                message = "The username and/or password you entered was invalid. Please try again."
                return render_template('login.html', message=message)  # Render login page with error message
            login_user(User(username))
            if 'url' in session and session['url']:
                url = session['url']
                session['url'] = None
                return redirect(url)  # Redirect to the target URL
            return redirect('/home')  # Redirect to home

    else:
        if current_user:
            if current_user.is_authenticated:
                return redirect('/home')
    return render_template('login.html', message=message)

@server.route('/logout', methods=['GET'])
def logout():
    if current_user:
        if current_user.is_authenticated:
            logout_user()
    return render_template('login.html')
@server.route('/')
def index_redirect():
    return redirect('/home')

# Login manager object will be used to log users in and out:
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"


class User(UserMixin):
    # User data model. It has to have at least self.id as a minimum
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    """This function loads the user by user id. Typically this looks up 
    the user from a user database. We won't be registering or looking up users 
    in this example, so we'll simply return a User object 
    with the passed-in username.
    """
    return User(username)

####################################################################################
####################################################################################
app = dash.Dash(__name__, server=server, use_pages=True, suppress_callback_exceptions=False,
                external_stylesheets=[dbc.themes.BOOTSTRAP])


# Main Navbar for department selection
@app.callback(
    Output('navbar', 'children'),
    Input('interval','n_intervals') # Use interval to trigger the callback -> access the current_user of Flask
)
def render_navbar(n_intervals):
    user_id = current_user.id
    permissions = VALID_USERNAME_PASSWORD[user_id]['permissions']
    navbar = dbc.Navbar(
        dbc.Container([
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src="assets/logos/white_logo.png", height="45px")), # Logo
                    dbc.Col(dbc.NavbarBrand("Dashboard",href="/home")),    # Home Page
                    dbc.Col(dbc.DropdownMenu(                          # Color-Mixing Department
                        children=[
                            dbc.DropdownMenuItem("Daily Report", href="/cm_daily", disabled=disable_page('cm_daily',permissions)),
                            dbc.DropdownMenuItem("Weekly Report", href="/cm_weekly", disabled=disable_page('cm_weekly',permissions)),
                            dbc.DropdownMenuItem("QC Loss Rate", href="/cm_qc", disabled=disable_page('cm_qc',permissions))
                        ],
                        nav=True,
                        in_navbar=True,
                        label="Color Mixing",
                    )),
                    dbc.Col(dbc.DropdownMenu(                          # Warehouse Department
                        children=[
                            dbc.DropdownMenuItem("全面的 - Tổng quát", href="/wh_overall", disabled=disable_page('wh_overall',permissions)),
                            dbc.DropdownMenuItem("客戶詳情 - Chi tiết khách hàng", href="/wh_customer", disabled=disable_page('wh_customer',permissions)),
                            dbc.DropdownMenuItem("客戶產品詳情 - Chi tiết SP của KH", href="/wh_product", disabled=disable_page('wh_product',permissions)),
                            dbc.DropdownMenuItem("預期交付和實際交付 - Dự định/Thực tế GH", href="/wh_plan", disabled=disable_page('wh_plan',permissions)),
                            dbc.DropdownMenuItem("比較 - So sánh", href="/wh_compare", disabled=disable_page('wh_compare',permissions)),
                            dbc.DropdownMenuItem("結論 - Kết luận", href="/wh_conclusion", disabled=disable_page('wh_conclusion',permissions)),
                            dbc.DropdownMenuItem("Dữ liệu", href="/wh_data", disabled=disable_page('wh_data',permissions))
                        ],
                        nav=True,
                        in_navbar=True,
                        label="倉庫-KHO",
                    )),
                    dbc.Col(dbc.DropdownMenu(                          # Sales Department
                        children=[
                            dbc.DropdownMenuItem("Daily Report", href="/s_daily", disabled=disable_page('s_daily',permissions)),
                            dbc.DropdownMenuItem("Weekly Report", href="/s_weekly", disabled=disable_page('s_weekly',permissions)),
                            dbc.DropdownMenuItem("Quy Trình", href="/s_systemsheet", disabled=disable_page('s_systemsheet',permissions)),
                            
                        ],
                        nav=True,
                        in_navbar=True,
                        label="Sales",
                    )),
                    dbc.Col(dbc.DropdownMenu(                          # Production Department
                        children=[
                            dbc.DropdownMenuItem("Daily Report", href="/prod_daily", disabled=disable_page('prod_daily',permissions)),
                            dbc.DropdownMenuItem("Weekly Report", href="/prod_weekly", disabled=disable_page('prod_weekly',permissions)),
                            
                        ],
                        nav=True,
                        in_navbar=True,
                        label="Production",
                    )),
                    dbc.Col(dbc.DropdownMenu(                          # R&D Department
                        children=[
                            dbc.DropdownMenuItem("Daily Report", href="/rd_daily", disabled=disable_page('rd_daily',permissions)),
                            dbc.DropdownMenuItem("Weekly Report", href="/rd_weekly", disabled=disable_page('rd_weekly',permissions)),
                            
                        ],
                        nav=True,
                        in_navbar=False,
                        label="RD",
                    )),
                ],
                class_name="left-side-navbar",

            ),

            dbc.Row([
                dbc.Col(dbc.NavItem(dbc.NavLink("SystemSheet", href="https://huge-eminently-lynx.ngrok-free.app"))),
                dbc.Col(html.A('Logout', href='/logout')),
            ],
            class_name="ml-auto right-side-navbar",)

        ]), color='#CC3333'
    )
    return navbar



def serve_layout():
    return html.Div([
    html.Div(id='navbar'),
    page_container,
    dcc.Interval(id='interval', interval=1, max_intervals=1)  # Trigger layout loading once
])

app.layout = serve_layout

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")