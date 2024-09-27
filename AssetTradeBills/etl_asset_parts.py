import psycopg2
import pandas as pd
from io import StringIO

# Function to convert only string columns to UTF-8
def convert_to_utf8(df):
    # Handle only object (string) columns
    for col in df.select_dtypes(include=[object]):
        df[col] = df[col].apply(lambda x: x.encode('utf-8', 'ignore').decode('utf-8') if isinstance(x, str) else x)
    
    return df

# Function to insert asset parts data into PostgreSQL
def insert_asset_parts(df, db):
    # Explicitly cast float64 columns to string before filling NaN values
    for col in df.select_dtypes(include=[float]):
        df[col] = df[col].astype(str)

    # Handle NaN values for timestamp columns by converting them to None (NULL in PostgreSQL)
    df.replace({pd.NA: None, 'nan': None}, inplace=True)

    # Create a string buffer to hold CSV data
    buffer = StringIO()

    # Write DataFrame to buffer (without headers)
    df.to_csv(buffer, index=False, header=False, na_rep='NULL')

    # Move the buffer cursor to the beginning
    buffer.seek(0)

    try:
        with db.cursor() as cursor:
            # Use copy_expert to insert the CSV data in bulk
            cursor.copy_expert('''
                COPY asset_parts (id, name, document_number, contact_email, contact_phone_number, deleted_at, created_at, updated_at, type)
                FROM STDIN
                WITH (FORMAT CSV, NULL 'NULL');
            ''', buffer)
        db.commit()
        print("Data inserted successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error inserting data: {e}")

# Load the CSV file into a DataFrame with mixed-type handling
dfAssetParts = pd.read_csv('asset_parts.csv', dtype=str)

# Convert all string columns to UTF-8 and handle NaN values properly
dfAssetParts = convert_to_utf8(dfAssetParts)

# Connect to your PostgreSQL database (replace credentials)
db = psycopg2.connect(dbname="postgres", user="postgres", password="123", host="localhost")

# Now proceed with inserting the data into PostgreSQL
insert_asset_parts(dfAssetParts, db)

# Close the database connection
db.close()