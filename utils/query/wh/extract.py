import pandas as pd
import calendar
from datetime import date
from utils.db import Database
pd.options.mode.chained_assignment = None



def get_mtd_by_month(selected_year, start_day, end_day, exclude_factory, table_name, agg_col, date_col):
    """
    A generic function to fetch aggregated metrics (sales or orders) from the database.
    
    Args:
        selected_year (int): The year to filter.
        start_day (int): The start day of the date range.
        end_day (int): The end day of the date range.
        exclude_factory (str): The factory to exclude.
        table_name (str): The name of the table to query (e.g., 'fact_sales' or 'fact_order').
        date_column (str): The date column to use for filtering (e.g., 'sales_date', 'order_date').

    Returns:
        pd.DataFrame: A DataFrame with the aggregated data.
    """
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
            query = f"""
                WITH filtered_dates AS (
                    SELECT date, month
                    FROM dim_date
                    WHERE day BETWEEN %(start_day)s AND %(end_day)s
                    AND year = %(selected_year)s
                )
                SELECT 
                    d.month,
                    SUM(CASE WHEN t.factory_code != %(exclude_factory)s THEN t.{agg_col} ELSE 0 END) AS sum_exclude,
                    SUM(CASE WHEN t.factory_code = %(exclude_factory)s THEN t.{agg_col} ELSE 0 END) AS sum_factory
                FROM {table_name} t
                JOIN filtered_dates d
                ON t.{date_col} = d.date
                GROUP BY d.month
                ORDER BY d.month;
            """
            cur.execute(query, {
                'selected_year': selected_year,
                'start_day': start_day,
                'end_day': end_day,
                'exclude_factory': exclude_factory
            })
            
            data = cur.fetchall()
            column_names = [description[0] for description in cur.description]
            df = pd.DataFrame(data=data, columns=column_names)
            return df
    finally:
        Database.return_connection(conn)




def extract_order_target(day_range, target_month, target_year):

    
    try:
        start_date = date(target_year, target_month, day_range[0])
        end_date = date(target_year, target_month, day_range[1])
    except:
        last_day = calendar.monthrange(target_year, target_month)[1]
        start_date = date(target_year, target_month, day_range[0])
        end_date = date(target_year, target_month, last_day)

    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
            cur.execute("""SELECT SUM(order_quantity)
                        FROM fact_order
                        WHERE factory_code != '30673'
                        AND order_date BETWEEN %(start_date)s AND %(end_date)s
                        """,
                        {'start_date': start_date, 'end_date': end_date})

            target = cur.fetchone()[0] or 0

            return target
    finally:
        Database.return_connection(conn)


def extract_sales_target(day_range, target_month, target_year):
    try:
        start_date = date(target_year, target_month, day_range[0])
        end_date = date(target_year, target_month, day_range[1])
    except:
        last_day = calendar.monthrange(target_year, target_month)[1]
        start_date = date(target_year, target_month, day_range[0])
        end_date = date(target_year, target_month, last_day)

    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
            cur.execute("""SELECT SUM(sales_quantity)
                        FROM fact_sales
                        WHERE factory_code != '30673'
                        AND sales_date BETWEEN %(start_date)s AND %(end_date)s
                        """,
                        {'start_date': start_date, 'end_date': end_date})

            target = cur.fetchone()[0] or 0

            return target
    finally:
        Database.return_connection(conn)

###############################################################
###############################################################
def get_mtd_factory_sales(start_date, end_date, start_date_target, end_date_target, THRESHOLD=1000):

    # Get product list
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
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
    finally:
        Database.return_connection(conn)



def get_total_sales(factory_list, target_year, target_month):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
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
    finally:
        Database.return_connection(conn)

##############################################################################
##############################################################################
def get_mtd_factory_order(start_date, end_date, start_date_target, end_date_target, THRESHOLD=1000):

    # Get product list
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
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
    finally:
        Database.return_connection(conn)



def get_total_order(factory_list, target_year, target_month):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
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
    finally:
        Database.return_connection(conn)

##############################################################################
##############################################################################



def get_mtd_product(start_date, end_date, start_date_target, end_date_target, factory_name):


    # Get product list
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
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
    finally:
        Database.return_connection(conn)


def get_table_value(active_cell, data):
    row = active_cell["row"]
    col_id = active_cell["column_id"]
    value = data[row][col_id]
    return value

def get_planned_deliveries(start_date, end_date, factory_list):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
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
    finally:
        Database.return_connection(conn)


def get_mom_1_factory(start_date, factory_name):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
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
    finally:
        Database.return_connection(conn)


def get_sales_all(start_date, end_date ,factory_name):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
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
    finally:
        Database.return_connection(conn)


#####################################################################################################
#####################################################################################################


def get_factory_list():
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
            cur.execute("""SELECT factory_code, factory_name
                        FROM dim_factory
                        """)
            data = cur.fetchall()
            column_names = [description[0] for description in cur.description]
            df = pd.DataFrame(data = data, columns = column_names)

            return df
    finally:
        Database.return_connection(conn)

def get_product_list():
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
            cur.execute("""SELECT product_code, product_name
                        FROM dim_product
                        """)
            
            data = cur.fetchall()
            column_names = [description[0] for description in cur.description]
            df = pd.DataFrame(data = data, columns = column_names)

            return df
    finally:
        Database.return_connection(conn)

def get_factory_code(factory_name):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
            cur.execute("""SELECT factory_code
                        FROM dim_factory
                        WHERE factory_name = %(factory_name)s
                        LIMIT 1
                        """,
                        {'factory_name': factory_name})

            return cur.fetchone()
    finally:
        Database.return_connection(conn)

def get_sales_same_month(start_date, end_date, start_date_target, end_date_target):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
            cur.execute("""SELECT d_sales.year, d_sales.month, SUM(s.sales_quantity),
                            CASE
                                WHEN d_sales.month = d_order.month THEN 'ĐĐH trong tháng'
                                ELSE 'ĐĐH cũ'
                            END AS is_same_month
                        FROM fact_sales s
                        JOIN fact_order o
                            ON s.order_code = o.order_code
                        JOIN dim_date d_sales
                            ON s.sales_date = d_sales.date
                        JOIN dim_date d_order
                            ON o.order_date = d_order.date
                        WHERE d_sales.date BETWEEN %(start_date)s AND %(end_date)s
                            OR d_sales.date BETWEEN %(start_date_target)s AND %(end_date_target)s
                        GROUP BY d_sales.year, d_sales.month, is_same_month""",
                        {'start_date':start_date, 'end_date':end_date,
                        'start_date_target':start_date_target, 'end_date_target':end_date_target})
            
            data = cur.fetchall()
            column_names = [description[0] for description in cur.description]
            df = pd.DataFrame(data = data, columns = column_names)

            return df
    finally:
        Database.return_connection(conn)


def get_color(value):
        return "green" if value > 0 else "red"
def get_text(value):
    return "增加TĂNG" if value > 0 else "减少GIẢM"

def get_max_sales_date():
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
            cur.execute("""SELECT MAX(sales_date)
                        FROM fact_sales""")
            max_sales_date = cur.fetchone()[0]
            return max_sales_date
    finally:
        Database.return_connection(conn)
    
def get_max_import_wh_timestamp():
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
            cur.execute("""SELECT MAX(import_wh_timestamp)
                        FROM fact_sales""")
            max_import_wh_timestamp = cur.fetchone()[0]
            return max_import_wh_timestamp
    finally:
        Database.return_connection(conn)

def get_all_row_order(start_date, end_date):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
            cur.execute("""SELECT * 
                        FROM fact_order o join dim_factory f
                        ON o.factory_code = f.factory_code
                        WHERE order_date BETWEEN %(start_date)s AND %(end_date)s""",
                        {'start_date': start_date, 'end_date': end_date})
            
            data = cur.fetchall()
            column_names = [description[0] for description in cur.description]
            df = pd.DataFrame(data = data, columns = column_names)
            return df
    finally:
        Database.return_connection(conn)


def get_all_row_sales(start_date, end_date):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
            cur.execute("""SELECT * 
                        FROM fact_sales s join dim_factory f
                        ON s.factory_code = f.factory_code
                        WHERE sales_date BETWEEN %(start_date)s AND %(end_date)s""",
                        {'start_date': start_date, 'end_date': end_date})

            data = cur.fetchall()
            column_names = [description[0] for description in cur.description]
            df = pd.DataFrame(data = data, columns = column_names)
            return df
    finally:
        Database.return_connection(conn)

def get_compare_sales_data(factory_name, product_name, list_year, time_groupby):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
            if factory_name == "全部 - Tất cả":
                factory_filter = ""
            else:
                factory_filter = f"WHERE factory_name = '{factory_name}'"

            if product_name == "全部 - Tất cả":
                product_filter = ""
            else:
                product_filter = f"WHERE product_name = '{product_name}'"

            query = f"""WITH filtered_factory AS (
                    SELECT factory_code
                    FROM dim_factory
                    {factory_filter}
                    ),
                    filtered_product AS (
                    SELECT product_code
                    FROM dim_product
                    {product_filter}
                    ),
                    filtered_date AS (
                    SELECT date, {time_groupby} AS agg_col, year
                    FROM dim_date
                    WHERE year IN %(list_year)s
                    )
                    SELECT year, agg_col, SUM(sales_quantity) as sales_quantity
                    FROM fact_sales s 
                    JOIN filtered_factory f ON s.factory_code = f.factory_code
                    JOIN filtered_product p ON s.product_code = p.product_code
                    JOIN filtered_date d ON s.sales_date = d.date
                    GROUP BY year, agg_col
                    ORDER BY year, agg_col
                    """
            
            cur.execute(query,
                        {'list_year': tuple(list_year)})

            data = cur.fetchall()
            column_names = [description[0] for description in cur.description]
            df = pd.DataFrame(data = data, columns = column_names)
            return df
    finally:
        Database.return_connection(conn)
        

def get_sales_ratio(selected_year):
    try:
        conn = Database.get_connection()
        with conn.cursor() as cur:
            cur.execute("""SELECT sum (sales_quantity) as sales_quantity, 
                        df.factory_code, df.factory_name, dd.year, dd.month, dp.product_type
                        FROM fact_sales fs
                            JOIN dim_date dd
                            ON fs.sales_date = dd.date
                            JOIN dim_factory df
                            ON fs.factory_code = df.factory_code
                            JOIN dim_product dp
                            ON fs.product_code = dp.product_code
                        WHERE dd.year = %(selected_year)s
                        GROUP BY df.factory_code, dd.year, dd.month, dp.product_type""",
                        {'selected_year': selected_year})

            data = cur.fetchall()
            column_names = [description[0] for description in cur.description]
            df = pd.DataFrame(data = data, columns = column_names)
            return df
    finally:
        Database.return_connection(conn)