import os
import shutil
from datetime import datetime
import pandas as pd
import numpy as np
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv
from .utils import insert_data, update_product_list, update_factory_list
load_dotenv()

def process_sales_file(file_path: str):
    print(f"Processing uploaded sales file: {file_path}")
    file_name = os.path.basename(file_path)

    # --- STAGING DB INSERT ---
    df = pd.read_excel(file_path)
    try:
        df.columns = ['sales_date', 'ct_date', 'sales_code', 'factory_code',
                      'factory_name', 'salesman', 'product_code', 'product_name', 'qc',
                      'warehouse_code', 'sales_quantity', 'order_code', 'import_code',
                      'note', 'factory_order_code']
    except:
        print("Column mismatch in Excel file.")
        return

    df.dropna(subset=['sales_code'], inplace=True)

    # Clean & transform
    df['sales_date'] = pd.to_datetime(df['sales_date'], dayfirst=True)
    df['ct_date'] = pd.to_datetime(df['ct_date'], dayfirst=True)
    df['factory_code'] = df['factory_code'].astype(str).str.replace(r'.0', '', regex=False)
    df["numerical_order"] = (df.groupby("sales_code").cumcount() + 1).astype(str).str.zfill(4)
    df["sales_code"] = df["sales_code"] + "  -" + df["numerical_order"]
    df = df.replace(np.nan, None)
    df['import_timestamp'] = datetime.now()

    # Add missing columns
    copr23_columns = [ ... ]  # You can paste the same list of expected columns from your script here
    for col in copr23_columns:
        if col not in df.columns:
            df[col] = None
    df = df[copr23_columns]

    # Insert to staging
    staging_conn = psycopg2.connect(
        database=os.getenv('STAGING_NAME'),
        user=os.getenv('STAGING_USER'),
        password=os.getenv('STAGING_PASSWORD'),
        host=os.getenv('STAGING_HOST'),
        port=os.getenv('STAGING_PORT')
    )
    staging_cur = staging_conn.cursor()
    insert_query = """ INSERT INTO copr23 (...) VALUES (%s, ..., %s) ON CONFLICT (sales_code) DO NOTHING; """
    for _, row in df.iterrows():
        try:
            staging_cur.execute(insert_query, tuple(row))
        except OperationalError as e:
            print(f"Insert error for sales_code {row['sales_code']}: {e}")
    staging_conn.commit()

    # Move processed file
    shutil.move(file_path, os.path.join(r"D:\VL1251\ETL\old_data\wh\sales", file_name))

    # --- WAREHOUSE LOAD ---
    wh_conn = psycopg2.connect(
        database=os.getenv('WAREHOUSE_NAME'),
        user=os.getenv('WAREHOUSE_USER'),
        password=os.getenv('WAREHOUSE_PASSWORD'),
        host=os.getenv('WAREHOUSE_HOST'),
        port=os.getenv('WAREHOUSE_PORT')
    )
    wh_cur = wh_conn.cursor()
    wh_cur.execute("SELECT MAX(import_timestamp) FROM fact_sales")
    latest_import = wh_cur.fetchone()[0]

    # Reconnect to staging to pull new rows
    staging_cur.execute("""SELECT product_code, ... FROM copr23 WHERE import_timestamp > %s""", (latest_import,))
    df_new = pd.DataFrame(staging_cur.fetchall(), columns=[desc[0] for desc in staging_cur.description])

    df_new['sales_date'] = pd.to_datetime(df_new['sales_date'], dayfirst=True)
    df_new['first_4_sales_code'] = df_new['sales_code'].str.split("-").str[0]
    df_new = df_new[df_new['first_4_sales_code'] == '2301']
    df_new.dropna(subset='qc', inplace=True)
    df_new.drop(columns=['first_4_sales_code'], inplace=True)

    # Fix KDT factory_code based on order_code
    df_KDT = df_new[df_new['factory_code'] == '30895.2'][['sales_code', 'factory_code', 'factory_order_code']]
    df_KDT.fillna("temp", inplace=True)
    df_KDT.loc[df_KDT['factory_order_code'].str.contains('ST', case=False, na=False), 'factory_code'] = "30895.1"
    df_KDT.loc[df_KDT['factory_order_code'].str.contains('TN', case=False, na=False), 'factory_code'] = "30895"
    df_KDT.loc[df_KDT['factory_order_code'].str.contains('BP', case=False, na=False), 'factory_code'] = "30895.5"
    df_KDT.loc[df_KDT['factory_order_code'].str.contains('QT', case=False, na=False), 'factory_code'] = "30895.4"
    df_KDT.columns = ['sales_code', 'factory_code_fixed', 'factory_order_code']
    df_new = df_new.merge(df_KDT[['sales_code', 'factory_code_fixed']], on='sales_code', how='left')
    df_new['factory_code'] = df_new['factory_code_fixed'].combine_first(df_new['factory_code'])
    df_new.drop(columns=['factory_code_fixed'], inplace=True)
    df_new['import_wh_timestamp'] = datetime.now()

    # Final load to warehouse
    insert_data(df_new, "fact_sales", wh_conn)

    # --- UPDATE DIM FACTORY ---
    staging_cur.execute("SELECT DISTINCT factory_code, factory_name FROM copr13 ORDER BY factory_code")
    df_factory = pd.DataFrame(staging_cur.fetchall(), columns=[desc[0] for desc in staging_cur.description])
    df_factory.drop_duplicates(subset='factory_code', inplace=True)
    df_factory['factory_code'] = df_factory['factory_code'].str.replace(r'.0', '', regex=False)

    for _, row in df_factory.iterrows():
        wh_cur.execute("""
            INSERT INTO dim_factory (factory_code, factory_name)
            VALUES (%s, %s)
            ON CONFLICT (factory_code)
            DO UPDATE SET factory_name = EXCLUDED.factory_name
        """, (row['factory_code'], row['factory_name']))
    wh_conn.commit()

    print("✅ File processed and loaded to data warehouse.")

# Usage:
# process_sales_file(r"D:\VL1251\dashboard\data\wh\sales\your_file.xlsx")



def process_order_file(file_path: str):
    file_name = os.path.basename(file_path)

    print(f"Processing file: {file_path}")
    print(datetime.today())

    try:
        df_copr13 = pd.read_excel(file_path)
        df_copr13.columns = ['order_date','ct_date','original_estimated_delivery_date','estimated_delivery_date',
                             'order_code','factory_code','factory_name','product_code',
                             'product_name','qc','order_quantity','delivered_quantity',
                             'factory_order_code','note','numerical_order','path','warehouse_type']
    except Exception as e:
        print(f"Error reading or renaming columns: {e}")
        return

    df_copr13.dropna(subset=['order_code','numerical_order'], inplace=True)

    # Format date columns
    df_copr13_date_cols = ['order_date','ct_date','estimated_delivery_date','original_estimated_delivery_date']
    for col in df_copr13_date_cols:
        df_copr13[col] = pd.to_datetime(df_copr13[col], dayfirst=True)

    # Format numerical order
    df_copr13['numerical_order'] = df_copr13['numerical_order'].astype(int).apply(lambda x: f"{int(float(x)):04}")
    df_copr13['order_code'] = df_copr13['order_code'] + "-" + df_copr13['numerical_order']

    df_copr13 = df_copr13.replace(np.nan, None)
    for col in df_copr13_date_cols:
        df_copr13[col] = df_copr13[col].astype(object).where(df_copr13[col].notnull(), None)

    df_copr13['import_timestamp'] = datetime.now()

    # Add missing columns
    copr13_columns = [...]  # keep your long copr13 column list here
    for col in copr13_columns:
        if col not in df_copr13.columns:
            df_copr13[col] = None
    df_copr13 = df_copr13[copr13_columns]

    staging_conn = psycopg2.connect(
        database=os.getenv('STAGING_NAME'),
        user=os.getenv('STAGING_USER'),
        password=os.getenv('STAGING_PASSWORD'),
        host=os.getenv('STAGING_HOST'),
        port=os.getenv('STAGING_PORT')
    )
    staging_cur = staging_conn.cursor()

    insert_query = """ 
        INSERT INTO copr13 (...) VALUES (...) 
        ON CONFLICT (order_code) DO UPDATE SET
        order_quantity = EXCLUDED.order_quantity,
        import_timestamp = EXCLUDED.import_timestamp;
    """  # Replace `...` with your actual query

    successful_inserts = []
    conflict_rows = []

    try:
        for _, row in df_copr13.iterrows():
            values = tuple(row)
            try:
                staging_cur.execute(insert_query, values)
                successful_inserts.append(row)
            except OperationalError as e:
                print(f"Conflict or error for {row['order_code']}: {e}")
                conflict_rows.append(row)
    except Exception as e:
        print(f"DB operation failed: {e}")
    staging_conn.commit()
    staging_conn.close()

    # Move file to archive
    shutil.move(file_path, os.path.join(r"D:\VL1251\ETL\old_data\wh\order", file_name))
    print("File moved to old folder")

    # Proceed to WAREHOUSE logic
    warehouse_conn = psycopg2.connect(
        database=os.getenv('WAREHOUSE_NAME'),
        user=os.getenv('WAREHOUSE_USER'),
        password=os.getenv('WAREHOUSE_PASSWORD'),
        host=os.getenv('WAREHOUSE_HOST'),
        port=os.getenv('WAREHOUSE_PORT')
    )
    warehouse_cur = warehouse_conn.cursor()
    warehouse_cur.execute("SELECT max(import_timestamp) FROM fact_order")
    latest_import = warehouse_cur.fetchone()[0]
    warehouse_conn.close()

    # Reconnect to staging
    staging_conn = psycopg2.connect(
        database=os.getenv('STAGING_NAME'),
        user=os.getenv('STAGING_USER'),
        password=os.getenv('STAGING_PASSWORD'),
        host=os.getenv('STAGING_HOST'),
        port=os.getenv('STAGING_PORT')
    )
    staging_cur = staging_conn.cursor()
    staging_cur.execute("""SELECT ... FROM copr13 WHERE import_timestamp > %(latest_import)s""",
                        {'latest_import': latest_import})  # Fill in SELECT columns
    data = staging_cur.fetchall()
    columns = [desc[0] for desc in staging_cur.description]
    df_copr13 = pd.DataFrame(data, columns=columns)
    staging_conn.close()

    for col in df_copr13_date_cols:
        df_copr13[col] = pd.to_datetime(df_copr13[col], dayfirst=True)
    df_copr13['first_4_order_code'] = df_copr13['order_code'].str.split("-").str[0]
    df_copr13 = df_copr13[df_copr13['first_4_order_code'] == '2201']
    df_copr13.dropna(subset='qc', inplace=True)
    df_copr13['factory_code'] = df_copr13['factory_code'].str.replace(r'.0', '', regex=False)
    df_copr13 = df_copr13.replace(np.nan, None)

    for col in df_copr13_date_cols:
        df_copr13[col] = df_copr13[col].astype(object).where(df_copr13[col].notnull(), None)
    df_copr13.drop(columns=['first_4_order_code'], inplace=True)

    # Factory code mapping logic
    df_KDT = df_copr13[df_copr13['factory_code'] == '30895.2'][['order_code', 'factory_code', 'factory_order_code']]
    df_KDT.fillna("temp", inplace=True)
    df_KDT.loc[df_KDT['factory_order_code'].str.contains('ST', case=False), 'factory_code'] = "30895.1"
    df_KDT.loc[df_KDT['factory_order_code'].str.contains('TN', case=False), 'factory_code'] = "30895"
    df_KDT.loc[df_KDT['factory_order_code'].str.contains('BP', case=False), 'factory_code'] = "30895.5"
    df_KDT.loc[df_KDT['factory_order_code'].str.contains('QT', case=False), 'factory_code'] = "30895.4"
    df_KDT.columns = ['order_code', 'factory_code_fixed', 'factory_order_code']

    df_copr13 = df_copr13.merge(df_KDT[['order_code', 'factory_code_fixed']], on='order_code', how='left')
    df_copr13['factory_code'] = df_copr13['factory_code_fixed'].combine_first(df_copr13['factory_code'])
    df_copr13.drop(columns=['factory_code_fixed'], inplace=True)

    df_copr13['import_wh_timestamp'] = datetime.now()

    # Load to warehouse
    warehouse_conn = psycopg2.connect(
        database=os.getenv('WAREHOUSE_NAME'),
        user=os.getenv('WAREHOUSE_USER'),
        password=os.getenv('WAREHOUSE_PASSWORD'),
        host=os.getenv('WAREHOUSE_HOST'),
        port=os.getenv('WAREHOUSE_PORT')
    )
    insert_data(df_copr13, "fact_order", warehouse_conn)
    warehouse_conn.close()

    update_product_list()
    update_factory_list()

    print("File processing completed.")