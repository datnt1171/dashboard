import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
import calendar
from dateutil.relativedelta import relativedelta
from datetime import date
load_dotenv()
pd.options.mode.chained_assignment = None

database_name = os.getenv('WAREHOUSE_NAME')
database_user = os.getenv('WAREHOUSE_USER')
database_password = os.getenv('WAREHOUSE_PASSWORD')
database_host = os.getenv('WAREHOUSE_HOST')
database_port = os.getenv('WAREHOUSE_PORT')



def get_overall_order(list_year):

    if isinstance(list_year, int):
        list_year = [list_year]

    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""SELECT order_date, factory_code, order_quantity, product_name, order_code
                FROM fact_order
                WHERE EXTRACT(YEAR FROM order_date) IN %(list_year)s
                """,
                {'list_year': tuple(list_year)})

    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df = pd.DataFrame(data = data, columns = column_names)
    return df


def get_overall_sales(list_year):

    if isinstance(list_year, int):
        list_year = [list_year]

    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""SELECT sales_date, factory_code, sales_quantity, product_name, order_code
                FROM fact_sales
                WHERE EXTRACT(YEAR FROM sales_date) IN %(list_year)s
                """,
                {'list_year': tuple(list_year)})

    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df = pd.DataFrame(data = data, columns = column_names)
    return df

def get_overall_planned(list_year):

    if isinstance(list_year, int):
        list_year = [list_year]

    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""SELECT estimated_delivery_date, factory_code, order_quantity, product_name
                FROM fact_order
                WHERE EXTRACT(YEAR FROM estimated_delivery_date) IN %(list_year)s
                """,
                {'list_year': tuple(list_year)})

    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df = pd.DataFrame(data = data, columns = column_names)
    return df


def extract_order_target(day_range, target_month, target_year):

    
    try:
        start_date = date(target_year, target_month, day_range[0])
        end_date = date(target_year, target_month, day_range[1])
    except:
        last_day = calendar.monthrange(target_year, target_month)[1]
        start_date = date(target_year, target_month, day_range[0])
        end_date = date(target_year, target_month, last_day)

    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""SELECT SUM(order_quantity)
                FROM fact_order
                WHERE factory_code != '30673'
                AND order_date BETWEEN %(start_date)s AND %(end_date)s
                """,
                {'start_date': start_date, 'end_date': end_date})

    target = cur.fetchone()[0] or 0

    return target


def extract_sales_target(day_range, target_month, target_year):
    try:
        start_date = date(target_year, target_month, day_range[0])
        end_date = date(target_year, target_month, day_range[1])
    except:
        last_day = calendar.monthrange(target_year, target_month)[1]
        start_date = date(target_year, target_month, day_range[0])
        end_date = date(target_year, target_month, last_day)

    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""SELECT SUM(sales_quantity)
                FROM fact_sales
                WHERE factory_code != '30673'
                AND sales_date BETWEEN %(start_date)s AND %(end_date)s
                """,
                {'start_date': start_date, 'end_date': end_date})

    target = cur.fetchone()[0] or 0

    return target







###############################################################
###############################################################
def get_mtd_factory_sales(start_date, end_date, start_date_target, end_date_target, THRESHOLD=1000):

    # Get product list
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""WITH factory_list AS (
                        SELECT DISTINCT factory_code, salesman
                        FROM fact_sales
                        WHERE 
                            (sales_date BETWEEN %(start_date)s AND %(end_date)s)
                            OR 
                            (sales_date BETWEEN %(start_date_target)s AND %(end_date_target)s)
                        
                    ),
                    current_month AS (
                        SELECT factory_code, SUM(sales_quantity) AS total_quantity
                        FROM fact_sales
                        WHERE sales_date BETWEEN %(start_date)s AND %(end_date)s
                        GROUP BY factory_code
                    ),
                    previous_month AS (
                        SELECT factory_code, SUM(sales_quantity) AS total_quantity_prev
                        FROM fact_sales
                        WHERE sales_date BETWEEN %(start_date_target)s AND %(end_date_target)s
                        GROUP BY factory_code
                    )
                    SELECT fl.factory_code, factory_name, salesman,
                        COALESCE(cm.total_quantity, 0) AS total_quantity, 
                        COALESCE(pm.total_quantity_prev, 0) AS total_quantity_prev
                    FROM factory_list fl
                    LEFT JOIN current_month cm ON fl.factory_code = cm.factory_code
                    LEFT JOIN previous_month pm ON fl.factory_code = pm.factory_code
                    LEFT JOIN dim_factory ON fl.factory_code = dim_factory.factory_code
                """,
                {'start_date': start_date, 'end_date': end_date,
                 'start_date_target': start_date_target, 'end_date_target': end_date_target})
    
    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df = pd.DataFrame(data = data, columns = column_names)


    df['quantity_diff'] = df['total_quantity'] - df['total_quantity_prev']
    df['quantity_diff_abs'] = df['quantity_diff'].abs()
    df['pct_change'] = df['quantity_diff'] / df['total_quantity_prev'] * 100

    df = df[df['quantity_diff_abs']>=THRESHOLD]

    return df



def get_total_sales(factory_list, target_year, target_month):
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""
        SELECT factory_code, SUM(sales_quantity) as sales_prev
        FROM fact_sales
        WHERE factory_code IN %(factory_list)s
            AND EXTRACT(YEAR FROM sales_date) = %(target_year)s
            AND EXTRACT(MONTH FROM sales_date) = %(target_month)s
        GROUP BY factory_code
    """, {'factory_list': tuple(factory_list), 'target_year': target_year, 'target_month': target_month})

    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df = pd.DataFrame(data = data, columns = column_names)
    return df

##############################################################################
##############################################################################
def get_mtd_factory_order(start_date, end_date, start_date_target, end_date_target, THRESHOLD=1000):

    # Get product list
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""WITH factory_list AS (
                        SELECT DISTINCT factory_code, salesman
                        FROM fact_order
                        WHERE order_date BETWEEN %(start_date)s AND %(end_date)s
                        OR order_date BETWEEN %(start_date_target)s AND %(end_date_target)s
                    ),
                    current_month AS (
                        SELECT factory_code, SUM(order_quantity) AS total_quantity
                        FROM fact_order
                        WHERE order_date BETWEEN %(start_date)s AND %(end_date)s
                        GROUP BY factory_code
                    ),
                    previous_month AS (
                        SELECT factory_code, SUM(order_quantity) AS total_quantity_prev
                        FROM fact_order
                        WHERE order_date BETWEEN %(start_date_target)s AND %(end_date_target)s
                        GROUP BY factory_code
                    )
                    SELECT fl.factory_code, factory_name, salesman,
                        COALESCE(cm.total_quantity, 0) AS total_quantity, 
                        COALESCE(pm.total_quantity_prev, 0) AS total_quantity_prev
                    FROM factory_list fl
                    LEFT JOIN current_month cm ON fl.factory_code = cm.factory_code
                    LEFT JOIN previous_month pm ON fl.factory_code = pm.factory_code
                    LEFT JOIN dim_factory ON fl.factory_code = dim_factory.factory_code
                """,
                {'start_date': start_date, 'end_date': end_date,
                 'start_date_target': start_date_target, 'end_date_target': end_date_target})
    
    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df = pd.DataFrame(data = data, columns = column_names)



    df['quantity_diff'] = df['total_quantity'] - df['total_quantity_prev']
    df['quantity_diff_abs'] = df['quantity_diff'].abs()
    df['pct_change'] = df['quantity_diff'] / df['total_quantity_prev'] * 100

    df = df[df['quantity_diff_abs']>=THRESHOLD]

    return df



def get_total_order(factory_list, target_year, target_month):
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""
                SELECT factory_code, SUM(order_quantity) as order_prev
                FROM fact_order
                WHERE factory_code IN %(factory_list)s
                    AND EXTRACT(YEAR FROM order_date) = %(target_year)s
                    AND EXTRACT(MONTH FROM order_date) = %(target_month)s
                GROUP BY factory_code
                """, 
                {'factory_list': tuple(factory_list), 'target_year': target_year, 'target_month': target_month})

    name_data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df_factory_name = pd.DataFrame(data = name_data, columns = column_names)
    return df_factory_name

##############################################################################
##############################################################################



def get_mtd_product(start_date, end_date, start_date_target, end_date_target, factory_name):


    # Get product list
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""WITH product_list AS (
                        SELECT DISTINCT product_name
                        FROM fact_sales JOIN dim_factory
                        ON fact_sales.factory_code = dim_factory.factory_code
                        WHERE factory_name = %(factory_name)s
                        AND (
                            (sales_date BETWEEN %(start_date)s AND %(end_date)s)
                            OR 
                            (sales_date BETWEEN %(start_date_target)s AND %(end_date_target)s)
                        )
                    ),
                    current_month AS (
                        SELECT product_name, SUM(sales_quantity) AS total_quantity
                        FROM fact_sales JOIN dim_factory
                        ON fact_sales.factory_code = dim_factory.factory_code
                        WHERE factory_name = %(factory_name)s
                        AND sales_date BETWEEN %(start_date)s AND %(end_date)s
                        GROUP BY product_name
                    ),
                    previous_month AS (
                        SELECT product_name, SUM(sales_quantity) AS total_quantity_prev
                        FROM fact_sales JOIN dim_factory
                        ON fact_sales.factory_code = dim_factory.factory_code
                        WHERE factory_name = %(factory_name)s
                        AND sales_date BETWEEN %(start_date_target)s AND %(end_date_target)s
                        GROUP BY product_name
                    )
                    SELECT pl.product_name,
                        COALESCE(cm.total_quantity, 0) AS total_quantity, 
                        COALESCE(pm.total_quantity_prev, 0) AS total_quantity_prev
                    FROM product_list pl
                    LEFT JOIN current_month cm ON pl.product_name = cm.product_name
                    LEFT JOIN previous_month pm ON pl.product_name = pm.product_name
                """,
                {'start_date': start_date, 'end_date': end_date,
                 'start_date_target': start_date_target, 'end_date_target': end_date_target,
                 'factory_name': factory_name})

    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df = pd.DataFrame(data = data, columns = column_names)
    return df


def get_table_value(active_cell, data):
    row = active_cell["row"]
    col_id = active_cell["column_id"]
    value = data[row][col_id]
    return value

def get_planned_deliveries(start_date, end_date, factory_list):
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""SELECT factory_code, SUM(order_quantity) AS planned_deliveries
            FROM fact_order
            WHERE estimated_delivery_date BETWEEN %(start_date)s AND %(end_date)s
            AND factory_code IN %(factory_list)s
            GROUP BY factory_code
            """,{'start_date': start_date, 'end_date': end_date ,'factory_list': tuple(factory_list)})

    planned_deliveries = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df_planned_deliveries = pd.DataFrame(data = planned_deliveries, columns = column_names)
    return df_planned_deliveries


def get_mom_1_factory(start_date, factory_name):
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""SELECT sales_date, sales_quantity
            FROM fact_sales JOIN dim_factory
                ON fact_sales.factory_code = dim_factory.factory_code
            WHERE EXTRACT(YEAR from sales_date) = %(start_year)s
                AND factory_name = %(factory_name)s
            """,{'start_year': start_date.year,'factory_name': factory_name})

    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df = pd.DataFrame(data = data, columns = column_names)
    return df


def get_sales_all(start_date, end_date ,factory_name):
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""SELECT product_name, SUM(sales_quantity) as sales_quantity
            FROM fact_sales JOIN dim_factory
                ON fact_sales.factory_code = dim_factory.factory_code
            WHERE sales_date BETWEEN %(start_date)s AND %(end_date)s
                AND factory_name = %(factory_name)s
            GROUP BY product_name
            """,{'start_date': start_date, 'end_date':end_date,'factory_name': factory_name})

    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df = pd.DataFrame(data = data, columns = column_names)
    return df


#####################################################################################################
#####################################################################################################


def get_factory_list():
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""SELECT factory_code, factory_name
                FROM dim_factory
                """)
    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df = pd.DataFrame(data = data, columns = column_names)

    return df

def get_product_list():
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""SELECT product_code, product_name
                FROM dim_product
                """)
    
    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df = pd.DataFrame(data = data, columns = column_names)

    return df


def get_sales_same_month(start_date, end_date, start_date_target, end_date_target):
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""SELECT sales_date, sales_quantity, order_date, s.factory_code
                FROM fact_sales s JOIN fact_order o 
                ON s.order_code = o.order_code
                WHERE sales_date BETWEEN %(start_date)s AND %(end_date)s
                OR sales_date BETWEEN %(start_date_target)s AND %(end_date_target)s""",
                {'start_date':start_date, 'end_date':end_date,
                 'start_date_target':start_date_target, 'end_date_target':end_date_target})
    
    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df = pd.DataFrame(data = data, columns = column_names)

    return df

def get_order_same_month(start_date, end_date, start_date_target, end_date_target):
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""SELECT order_date, order_quantity, factory_code
                FROM fact_order
                WHERE order_date BETWEEN %(start_date)s AND %(end_date)s
                OR order_date BETWEEN %(start_date_target)s AND %(end_date_target)s""",
                {'start_date':start_date, 'end_date':end_date,
                 'start_date_target':start_date_target, 'end_date_target':end_date_target})
    
    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df = pd.DataFrame(data = data, columns = column_names)

    return df

def get_color(value):
        return "green" if value > 0 else "red"
def get_text(value):
    return "增加TĂNG" if value > 0 else "减少GIẢM"

def get_max_sales_date():
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""SELECT MAX(sales_date)
                FROM fact_sales""")
    return cur.fetchone()[0]
    
def get_max_import_wh_timestamp():
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""SELECT MAX(import_wh_timestamp)
                FROM fact_sales""")
    return cur.fetchone()[0]

def get_all_row_order(start_date, end_date):
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()

    cur.execute("""SELECT * 
                FROM fact_order o join dim_factory f
                ON o.factory_code = f.factory_code
                WHERE order_date BETWEEN %(start_date)s AND %(end_date)s""",
                {'start_date': start_date, 'end_date': end_date})
    
    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df = pd.DataFrame(data = data, columns = column_names)
    return df


def get_all_row_sales(start_date, end_date):
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()

    cur.execute("""SELECT * 
                FROM fact_sales s join dim_factory f
                ON s.factory_code = f.factory_code
                WHERE sales_date BETWEEN %(start_date)s AND %(end_date)s""",
                {'start_date': start_date, 'end_date': end_date})

    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df = pd.DataFrame(data = data, columns = column_names)
    return df