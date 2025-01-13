from psycopg2 import pool

class Database:
    _pool = None

    @staticmethod
    def initialize(database, user, password, host, port, minconn=1, maxconn=10):
        Database._pool = pool.SimpleConnectionPool(
            minconn, maxconn,
            database=database, user=user, password=password,
            host=host, port=port
        )

    @staticmethod
    def get_connection():
        if Database._pool is None:
            raise Exception("Connection pool is not initialized. Call initialize() first.")
        return Database._pool.getconn()

    @staticmethod
    def return_connection(conn):
        Database._pool.putconn(conn)

    @staticmethod
    def close_all_connections():
        if Database._pool:
            Database._pool.closeall()
