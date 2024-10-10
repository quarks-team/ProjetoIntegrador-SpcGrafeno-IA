# app/repositories/database.py

import psycopg2

class PostgresConnection:
    def __init__(self, host, port, user, password, dbname):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.connection = None

    def __enter__(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.dbname
            )
            self.connection.autocommit = True
            print("Connection established")
        except Exception as e:
            print(f"Error connecting to the database: {e}")
        return self

    def execute_query(self, query, values=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                print("Query executed successfully")
        except Exception as e:
            print(f"Error executing query: {e}")

    def fetch_results(self, query, values=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                result = cursor.fetchall()
                return result
        except Exception as e:
            print(f"Error fetching results: {e}")
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()
            print("Connection closed")
