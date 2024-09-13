import psycopg2

class PostgresConnection:
    def __init__(self, dbname, user, password, host='localhost'):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.conn = None
        self.cursor = None

    def connect(self):
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host)
                self.cursor = self.conn.cursor()
                print("Connection established.")
            except Exception as e:
                print(f"Error connecting to the database: {e}")
                raise e  # Re-raise the exception for higher-level handling

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()  # Commit the transaction
        except Exception as e:
            print(f"Error executing query: {e}")
            self.conn.rollback()  # Rollback the transaction on error
            raise e  # Re-raise the exception for handling

    def fetchone(self):
        try:
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error fetching one record: {e}")
            raise e

    def fetchall(self):
        try:
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching all records: {e}")
            raise e

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Connection closed.")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if exc_type:
            print(f"Exception occurred: {exc_val}")
