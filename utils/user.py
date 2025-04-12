import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
pd.options.mode.chained_assignment = None

database_name = os.getenv('WAREHOUSE_NAME')
database_user = os.getenv('WAREHOUSE_USER')
database_password = os.getenv('WAREHOUSE_PASSWORD')
database_host = os.getenv('WAREHOUSE_HOST')
database_port = os.getenv('WAREHOUSE_PORT')




def get_users():
    dict_role = {'admin': ['wh_overall', 'wh_customer' ,'wh_product','wh_plan','wh_compare','wh_conclusion','wh_data',
                       'cm_daily','cm_weekly','cm_qc',
                       's_daily','s_weekly','s_systemsheet',
                       'prod_daily','prod_weekly',
                       'rd_daily','rd_weekly'],
                       
             'warehouse': ['wh_overall', 'wh_customer' ,'wh_product','wh_plan','wh_compare','wh_conclusion','wh_data'],
             'color_mixing': ['cm_daily','cm_weekly','cm_qc'],
             'sales': ['s_daily','s_weekly','s_systemsheet'],
             'production': ['prod_daily','prod_weekly'],
             'rd': ['rd_daily','rd_weekly'],
             'test': ['wh_overall', 'wh_customer' ,'wh_product','wh_plan','wh_compare','wh_conclusion',
                       'cm_daily','cm_weekly','cm_qc',]}
    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            , host=database_host, port=database_port)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM users""")

    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df_user = pd.DataFrame(data = data, columns = column_names)
    df_user['permissions'] = df_user['role'].map(lambda x: dict_role.get(x, []))
    return df_user


