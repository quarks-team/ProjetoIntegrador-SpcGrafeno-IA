import pandas as pd
import sys
import os
from datetime import datetime

from app.repositories.database import PostgresConnection

# Function to transform the data
def transform_data(df):
    # Create the 'installment' column: difference between due_date and created_at in months
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['due_date'] = pd.to_datetime(df['due_date'])
    df['installment'] = ((df['due_date'] - df['created_at']).dt.days / 30).astype(int)
    
    # Create 'month_due_date' and 'quarter_due_date' columns from due_date
    df['month_due_date'] = df['due_date'].dt.month
    df['quarter_due_date'] = df['due_date'].dt.quarter

    # Perform One-Hot Encoding for categorical fields
    payment_place_dummies = pd.get_dummies(df['payment_place'], prefix='payment_place')
    segmento_dummies = pd.get_dummies(df['segmento'], prefix='segmento')
    kind_dummies = pd.get_dummies(df['kind'], prefix='kind')

    # Concatenate the dummy columns to the original dataframe
    df = pd.concat([df, payment_place_dummies, segmento_dummies, kind_dummies], axis=1)

    # Create the 'result' column: 1 if duplicate is finished, 0 if canceled
    df['result'] = df['status'].apply(lambda x: 1 if x == 'finished' else 0 if x == 'canceled' else None)

    # Filter only finished or canceled duplicates
    df = df[df['status'].isin(['finished', 'canceled'])]

    return df

# Function to load transformed data into the database
def load_data_to_db(df, connection):
    # Insert the transformed data into the database
    insert_query = """
    INSERT INTO ia_score_data (
        score_entry_id, supplier_reference_id, installment, month_due_date, quarter_due_date,
        payment_place_state_1, payment_place_state_2, segmento_products, segmento_services,
        kind_type_1, kind_type_2, result
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    
    test =  PostgresConnection(
        
    )
    test.__enter__()

    for _, row in df.iterrows():
        values = (
            row['id'], row['supplier_reference_id'], row['installment'], row['month_due_date'],
            row['quarter_due_date'], row['payment_place_state_1'], row['payment_place_state_2'],
            row['segmento_products'], row['segmento_services'], row['kind_type_1'],
            row['kind_type_2'], row['result']
        )
        test.execute_query(insert_query, values)

# Main ETL function
def run_etl(input_file):
    # Load the data
    df = pd.read_excel(input_file)

    # Transform the data
    transformed_df = transform_data(df)

    # Connect to the database and load the transformed data
    with PostgresConnection() as connection:
        load_data_to_db(transformed_df, connection)

# Execute the ETL with the input file
if __name__ == "__main__":
    input_file = 'C:\\Users\\Noite\\Desktop\\ProjetoIntegrador-SpcGrafeno-IA\\old_table.xlsx'
    run_etl(input_file)
