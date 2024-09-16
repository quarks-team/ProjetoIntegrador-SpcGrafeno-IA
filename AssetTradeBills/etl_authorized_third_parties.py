import psycopg2
import pandas as pd
from io import StringIO

# Function to convert only string columns to UTF-8
def convert_to_utf8(df):
    # Handle only object (string) columns
    for col in df.select_dtypes(include=[object]):
        df[col] = df[col].apply(lambda x: x.encode('utf-8', 'ignore').decode('utf-8') if isinstance(x, str) else x)
    
    return df

# Function to insert data into the participant_authorized_third_parties table
def insert_participant_authorized_third_parties(df, db):
    # Explicitly cast float64 columns to string before filling NaN values
    for col in df.select_dtypes(include=[float]):
        df[col] = df[col].astype(str)

    # Handle NaN values by replacing them with None
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
                COPY participant_authorized_third_parties (id, participant_id, authorized_third_party_id, created_at, updated_at, state, approved_at, rejected_at)
                FROM STDIN
                WITH (FORMAT CSV, NULL 'NULL');
            ''', buffer)
        db.commit()
        print("Data inserted successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error inserting data: {e}")

# Load the CSV file into a DataFrame with mixed-type handling
dfParticipantAuthorizedThirdParties = pd.read_csv('participant_authorized_third_parties.csv', dtype=str)

# Convert all string columns to UTF-8 and handle NaN values properly
dfParticipantAuthorizedThirdParties = convert_to_utf8(dfParticipantAuthorizedThirdParties)

# Connect to your PostgreSQL database (replace credentials)
db = psycopg2.connect(dbname="postgres", user="postgres", password="123", host="localhost")

# Insert the data into PostgreSQL
insert_participant_authorized_third_parties(dfParticipantAuthorizedThirdParties, db)

# Close the database connection
db.close()
