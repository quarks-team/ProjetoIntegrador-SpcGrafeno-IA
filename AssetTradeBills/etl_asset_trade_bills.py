import psycopg2
import pandas as pd
from psycopg2 import sql

# Function to insert asset trade bills data into PostgreSQL
def insert_asset_trade_bills(df, db):
    with db.cursor() as cursor:
        for index, row in df.iterrows():
            try:
                # Construct the SQL query dynamically
                columns = df.columns.tolist()
                query = sql.SQL('''
                    INSERT INTO asset_trade_bills ({})
                    VALUES ({})
                ''').format(
                    sql.SQL(', ').join(map(sql.Identifier, columns)),
                    sql.SQL(', ').join(sql.Placeholder() * len(columns))
                )
                
                # Execute the insert query with the row values
                cursor.execute(query, tuple(row))
                db.commit()
                print(f"Row {index} inserted successfully.")

            except psycopg2.IntegrityError as e:
                db.rollback()
                print(f"Error inserting row {index}: {e}")
            
            except Exception as e:
                db.rollback()
                print(f"Unexpected error inserting row {index}: {e}")

# Load the CSV file into a DataFrame
dfAssetTradeBills = pd.read_csv('asset_trade_bills.csv', dtype=str)

# Connect to your PostgreSQL database (replace credentials)
db = psycopg2.connect(dbname="postgres", user="postgres", password="123", host="localhost")

# Insert the data into PostgreSQL
insert_asset_trade_bills(dfAssetTradeBills, db)

# Close the database connection
db.close()
