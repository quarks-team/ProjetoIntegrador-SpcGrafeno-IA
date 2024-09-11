import psycopg2
from psycopg2 import sql, extras

class PostgresConnection:
    def __init__(self, dbname, user, password, host='localhost', port=5432):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish a connection to the PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.conn.cursor(cursor_factory=extras.RealDictCursor)
            print("Connection established.")
        except psycopg2.Error as e:
            print(f"Unable to connect to the database. Error: {e}")

    def close(self):
        """Close the connection and cursor."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Connection closed.")

    def execute_query(self, query, params=None):
        """Execute a query against the database."""
        if not self.conn or not self.cursor:
            raise Exception("Connection not established. Please call connect() first.")
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            print("Query executed successfully.")
        except psycopg2.Error as e:
            print(f"Error executing query: {e}")

    def fetch_query(self, query, params=None):
        """Execute a query and fetch all results."""
        if not self.conn or not self.cursor:
            raise Exception("Connection not established. Please call connect() first.")
        try:
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            return results
        except psycopg2.Error as e:
            print(f"Error fetching query results: {e}")
            return None


