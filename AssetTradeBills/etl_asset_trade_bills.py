import psycopg2
import pandas as pd
from io import StringIO

def insert_asset_trade_bills(df, db):
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
            # Use copy_expert to insert the CSV data in bulk
            cursor.copy_expert('''
                COPY asset_trade_bills (
                    id, due_date, nfe_number, nfe_series, kind, state, payer_id, 
                    endorser_original_id, new_due_date, participant_id, ballast_kind, 
                    invoice_number, payment_place, update_reason_kind, finished_at
                )
                FROM STDIN
                WITH (FORMAT CSV);
            ''', buffer)
        db.commit()
        print("Data inserted successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error inserting data: {e}")

def convert_to_utf8(df):
    # Handle string columns
    for col in df.select_dtypes(include=[object]):
        df[col] = df[col].apply(lambda x: x.encode('utf-8', 'ignore').decode('utf-8') if pd.notna(x) else '')

    # Handle numeric and other non-string columns by replacing NaN with None
    for col in df.select_dtypes(exclude=[object]):
        df[col] = df[col].apply(lambda x: None if pd.isna(x) else x)

    return df

# Load the DataFrame
dfAssetTradeBills = pd.read_csv('asset_trade_bills.csv')

# Convert all string columns to UTF-8 and handle NaN values properly
dfAssetTradeBills = convert_to_utf8(dfAssetTradeBills)

# Connect to your PostgreSQL database
db = psycopg2.connect(dbname="postgres", user="postgres", password="123", host="localhost")

# Now proceed with inserting the data into PostgreSQL
insert_asset_trade_bills(dfAssetTradeBills, db)

# Close the database connection
db.close()
