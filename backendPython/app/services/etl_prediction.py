import pandas as pd
from datetime import datetime
from app.repositories.database import PostgresConnection

# Função para transformar os dados
def transform_data(df):
    # Criar a coluna installment: diferença entre due_date e created_at em meses
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['due_date'] = pd.to_datetime(df['due_date'])
    df['installment'] = ((df['due_date'] - df['created_at']).dt.days / 30).astype(int)
    
    # Criar colunas month_due_date e quarter_due_date a partir de due_date
    df['month_due_date'] = df['due_date'].dt.month
    df['quarter_due_date'] = df['due_date'].dt.quarter

    # Realizar One-Hot Encoding para os campos categóricos
    payment_place_dummies = pd.get_dummies(df['payment_place'], prefix='payment_place')
    segmento_dummies = pd.get_dummies(df['segmento'], prefix='segmento')
    kind_dummies = pd.get_dummies(df['kind'], prefix='kind')

    # Concatenar os dummies ao dataframe original
    df = pd.concat([df, payment_place_dummies, segmento_dummies, kind_dummies], axis=1)

    # Criar a coluna result: 1 se duplicata foi finalizada, 0 se cancelada
    df['result'] = df['status'].apply(lambda x: 1 if x == 'finished' else 0 if x == 'canceled' else None)

    # Filtrar apenas as duplicatas finalizadas ou canceladas
    df = df[df['status'].isin(['finished', 'canceled'])]

    return df

# Função para carregar os dados transformados no banco de dados
def load_data_to_db(df, connection):
    # Inserir os dados transformados no banco
    insert_query = """
    INSERT INTO ia_score_data (
        score_entry_id, supplier_reference_id, installment, month_due_date, quarter_due_date,
        payment_place_state_1, payment_place_state_2, segmento_products, segmento_services,
        kind_type_1, kind_type_2, result
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    for _, row in df.iterrows():
        values = (
            row['id'], row['supplier_reference_id'], row['installment'], row['month_due_date'],
            row['quarter_due_date'], row['payment_place_state_1'], row['payment_place_state_2'],
            row['segmento_products'], row['segmento_services'], row['kind_type_1'],
            row['kind_type_2'], row['result']
        )
        connection.execute_query(insert_query, values)

# Função principal do ETL
def run_etl(input_file):
    # Carregar os dados
    df = pd.read_excel(input_file)

    # Transformar os dados
    transformed_df = transform_data(df)

    # Conectar ao banco e carregar os dados transformados
    with PostgresConnection() as connection:
        load_data_to_db(transformed_df, connection)

# Executar o ETL com o arquivo de entrada
if __name__ == "__main__":
    input_file = 'C:\\Users\\Noite\\Desktop\\ProjetoIntegrador-SpcGrafeno-IA\\old_table.xlsx'
    run_etl(input_file)
