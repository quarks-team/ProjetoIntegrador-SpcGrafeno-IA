import psycopg2
import pandas as pd
from io import StringIO
import numpy as np

def insert_paymasters(df, db):
    # Create a string buffer to hold CSV data
    buffer = StringIO()
    
    # Handle NaN values and convert DataFrame to CSV format
    df.fillna('', inplace=True)
    
    # Write DataFrame to buffer
    df.to_csv(buffer, index=False, header=False)
    
    # Move the buffer cursor to the beginning
    buffer.seek(0)

    try:
        with db.cursor() as cursor:
            # Use copy_from to insert the CSV data in bulk
            cursor.copy_expert('''
                COPY paymasters (id, kind, name, document, email_primary, email_secondary, deleted_at, created_at, updated_at)
                FROM STDIN
                WITH (FORMAT CSV);
            ''', buffer)
        db.commit()
        print("Data inserted successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error inserting data: {e}")

# Example usage:
# Load the DataFrame
dfPaymasters = pd.read_csv('paymasters.csv')

# Connect to your PostgreSQL database
db = psycopg2.connect(dbname="postgres", user="postgres", password="123", host="localhost")

def convert_to_utf8(df):
    # Handle string columns
    for col in df.select_dtypes(include=[object]):
        df[col] = df[col].apply(lambda x: x.encode('utf-8', 'ignore').decode('utf-8') if pd.notna(x) else '')

    # Handle numeric and other non-string columns by replacing NaN with None
    for col in df.select_dtypes(exclude=[object]):
        df[col] = df[col].apply(lambda x: None if pd.isna(x) else x)

    return df

# Load your CSV file into a DataFrame
dfPaymasters = pd.read_csv('paymasters.csv')

# Convert all string columns to UTF-8 and handle NaN values properly
dfPaymasters = convert_to_utf8(dfPaymasters)

# Now proceed with inserting the data into PostgreSQL
insert_paymasters(dfPaymasters, db)