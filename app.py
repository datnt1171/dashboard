import dash
import dash_bootstrap_components as dbc
from dash import html, page_container, dcc

from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
import dash_auth

import warnings
warnings.filterwarnings("ignore") 

# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = {
    'dat': '123',
    'stanley': '123',
    'dungtq': '123',
    'banv': '123'
}






# Initialize Flask app
# server = Flask(__name__)
# server.secret_key = 'your_secret_key'

# # Setup Flask-Login
# login_manager = LoginManager()
# login_manager.init_app(server)
# login_manager.login_view = 'login'

# # User class for authentication
# class User(UserMixin):
#     def __init__(self, id):
#         self.id = id

# # A dictionary to store user credentials (for demo purposes)
# # You can use a database in production
# users = {'dat': {'password': 'lkjhgnhI1@'},
#          'stanley': {'password': '123'}}

# @login_manager.user_loader
# def load_user(user_id):
#     return User(user_id)

# # Route for login
# @server.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         if username in users and users[username]['password'] == password:
#             user = User(username)
#             login_user(user)
#             return redirect('/')
#         else:
#             return 'Invalid credentials', 401
#     return render_template('login.html')

# # Route for logout
# @server.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('login'))

# # Protect the dash app with login requirement
# @server.route('/')
# @login_required
# def dashboard():
#     return app.index()  # Protects access to the Dash app

#server=server,url_base_pathname='/',

# Initialize the Dash app
app = dash.Dash(__name__, use_pages=True,  external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
app.server.secret_key = 'your_secret_key_here1@'
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)
PLOTLY_LOGO = "/assets/white_logo.png"

# Main Navbar for department selection

navbar = dbc.Navbar(
    dbc.Container([
        # Use row and col to control vertical alignment of logo / brand
        dbc.Row(
            [
                dbc.Col(html.Img(src=PLOTLY_LOGO, height="45px")), # Logo
                dbc.Col(dbc.NavbarBrand("Dashboard",href="/")),    # Home Page
                dbc.Col(dbc.DropdownMenu(                          # Color-Mixing Department
                    children=[
                        dbc.DropdownMenuItem("Daily Report", href="/color_mixing_daily"),
                        dbc.DropdownMenuItem("Weekly Report", href="/color_mixing_weekly"),
                        dbc.DropdownMenuItem("QC Loss Rate", href="/color_mixing_qc")
                    ],
                    nav=True,
                    in_navbar=True,
                    label="Color Mixing",
                )),
                dbc.Col(dbc.DropdownMenu(                          # Warehouse Department
                    children=[
                        dbc.DropdownMenuItem("全面的 - Tổng quát", href="/warehouse_overall"),
                        dbc.DropdownMenuItem("所有客戶 - Tất cả khách hàng", href="/warehouse_mom"),
                        dbc.DropdownMenuItem("客戶產品詳情 - Chi tiết SP của KH", href="/warehouse_factory"),
                        dbc.DropdownMenuItem("預期交付和實際交付 - Dự định/Thực tế GH", href="/delivered_percentage"),
                        dbc.DropdownMenuItem("比較 - So sánh", href="/warehouse_drilldown"),
                        dbc.DropdownMenuItem("結論 - Kết luận", href="/warehouse_conclusion")
                    ],
                    nav=True,
                    in_navbar=True,
                    label="倉庫-KHO",
                )),
                dbc.Col(dbc.DropdownMenu(                          # Sales Department
                    children=[
                        dbc.DropdownMenuItem("Weekly Report", href="#"),
                        dbc.DropdownMenuItem("Test", href="#"),
                        
                    ],
                    nav=True,
                    in_navbar=True,
                    label="Sales",
                    disabled=True
                )),
                dbc.Col(dbc.DropdownMenu(                          # Production Department
                    children=[
                        dbc.DropdownMenuItem("Weekly Report", href="#"),
                        dbc.DropdownMenuItem("Test", href="#"),
                        
                    ],
                    nav=True,
                    in_navbar=True,
                    label="Production",
                    disabled=True
                )),
                dbc.Col(dbc.DropdownMenu(                          # R&D Department
                    children=[
                        dbc.DropdownMenuItem("Weekly Report", href="#"),
                        dbc.DropdownMenuItem("Test", href="#"),
                        
                    ],
                    nav=True,
                    in_navbar=False,
                    label="RD",
                    disabled=True
                )),
            ],
            class_name="left-side-navbar",

        ),

        dbc.Row([
            dbc.Col(dbc.NavItem(dbc.NavLink("System Sheet", href="https://huge-eminently-lynx.ngrok-free.app")))
        ],
        class_name="ml-auto right-side-navbar",)
        
        
    ]), color='#CC3333'
)



# Main layout with navbar and page container
app.layout = html.Div([
    # dcc.Store(id="mom_table_sales_increase_store", data={}),
    # dcc.Store(id="mom_table_sales_decrease_store", data={}),
    navbar,
    page_container  # Dynamically renders the page content based on URL
])

# Run the app
if __name__ == '__main__':
    app.run(debug=True)



# server.run