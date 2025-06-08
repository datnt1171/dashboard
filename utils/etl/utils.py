def insert_data(df_data, table_name, conn):
    """
    Inserts data from a DataFrame into a specified PostgreSQL table.

    Parameters:
    df_data (pd.DataFrame): DataFrame containing the data to insert.
    conn (psycopg2 connection): Active connection to the PostgreSQL database.
    table_name (str): The name of the table to insert data into.
    """
    try:
        # Get the column names from the DataFrame
        columns = list(df_data.columns)

        # Create the SQL insert query dynamically based on column names
        insert_query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES ({', '.join(['%s'] * len(columns))});
        """

        # Convert the DataFrame to a list of tuples (for batch insert)
        data = [tuple(row[1:]) for row in df_data.itertuples()]

        # Execute the batch insert
        cur = conn.cursor()
        cur.executemany(insert_query, data)
        conn.commit()

        print("Data inserted successfully!")
    except Exception as e:
        conn.rollback()  # Rollback in case of any error
        print(f"An error occurred: {e}")
        
def update_product_list():
    import pandas as pd
    import psycopg2
    import os
    from dotenv import load_dotenv
    load_dotenv()

    # Connect to Warehouse
    database_name = os.getenv('WAREHOUSE_NAME')
    database_user = os.getenv('WAREHOUSE_USER')
    database_password = os.getenv('WAREHOUSE_PASSWORD')
    database_host = os.getenv('WAREHOUSE_HOST')
    database_port = os.getenv('WAREHOUSE_PORT')

    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            ,host=database_host, port=database_port)
    cur = conn.cursor()

    cur.execute("""SELECT DISTINCT product_code, product_name
                FROM fact_sales""")
    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df_product = pd.DataFrame(data = data, columns = column_names)


    # Upsert query
    upsert_query = """
    INSERT INTO dim_product (product_code, product_name)
    VALUES (%s, %s)
    ON CONFLICT (product_code) 
    DO UPDATE SET 
        product_name = EXCLUDED.product_name;
    """

    # Execute the upsert for each row in data
    for _, row in df_product.iterrows():  # Iterate over rows as (index, Series)
        cur.execute(upsert_query, (row["product_code"], row["product_name"]))
    # Commit changes
    conn.commit()
    print('Dim product updated')
    
def update_factory_list():
    import pandas as pd
    import psycopg2
    import os
    from dotenv import load_dotenv
    load_dotenv()

    database_name = os.getenv('STAGING_NAME')
    database_user = os.getenv('STAGING_USER')
    database_password = os.getenv('STAGING_PASSWORD')
    database_host = os.getenv('STAGING_HOST')
    database_port = os.getenv('STAGING_PORT')

    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            ,host=database_host, port=database_port)
    cur = conn.cursor()

    cur.execute("""SELECT DISTINCT factory_code, factory_name
                FROM copr13
                ORDER BY factory_code""")
    data = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    df_factory = pd.DataFrame(data = data, columns = column_names)

    df_factory.drop_duplicates(subset='factory_code', inplace=True)
    df_factory['factory_code'] = df_factory['factory_code'].str.replace(r'.0','', regex=False)
    # Connect to Warehouse
    database_name = os.getenv('WAREHOUSE_NAME')
    database_user = os.getenv('WAREHOUSE_USER')
    database_password = os.getenv('WAREHOUSE_PASSWORD')
    database_host = os.getenv('WAREHOUSE_HOST')
    database_port = os.getenv('WAREHOUSE_PORT')

    conn = psycopg2.connect(database=database_name, user=database_user, password=database_password
                            ,host=database_host, port=database_port)
    cur = conn.cursor()
    # Upsert query
    upsert_query = """
    INSERT INTO dim_factory (factory_code, factory_name)
    VALUES (%s, %s)
    ON CONFLICT (factory_code)
    DO UPDATE SET
        factory_name = EXCLUDED.factory_name;
    """

    # Execute the upsert for each row in data
    for _, row in df_factory.iterrows():  
        cur.execute(upsert_query, (row["factory_code"], row["factory_name"]))

    # Commit changes
    conn.commit()
    print('Dim factory updated')