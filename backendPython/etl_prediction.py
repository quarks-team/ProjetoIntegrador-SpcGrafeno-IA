import pandas as pd
import logging
from datetime import datetime
from app.repositories.database import PostgresConnection

# Configuração de logs
logging.basicConfig(filename="insercao_dados.log", level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Função para detectar segmentos dentro dos dados de duplicatas
def detectar_segmentos(df, endossantes_ids):
    segmentos = []

    for idx, row in df.iterrows():
        nome_lower = str(row['name']).lower()
        if row['id'] in endossantes_ids:
            segmentos.append("Endossante")
        elif any(word in nome_lower for word in ["stg", "fidc", "investimento", "investimentos", "fgts", "finan", "invest", "credito"]):
            segmentos.append("Fundo")
        elif "teste" in nome_lower:
            segmentos.append("Outros")
        else:
            segmentos.append("Comércio")
    
    df['segmento'] = segmentos
    return df

# Função para transformar os dados
def transform_data(df, endossantes_ids):
    df = detectar_segmentos(df, endossantes_ids)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['due_date'] = pd.to_datetime(df['due_date'])
    df['installment'] = ((df['due_date'] - df['created_at']).dt.days / 30).astype(int)
    df['month_due_date'] = df['due_date'].dt.month
    df['quarter_due_date'] = df['due_date'].dt.quarter

    payment_place_dummies = pd.get_dummies(df['payment_place'], prefix='payment_place')
    segmento_dummies = pd.get_dummies(df['segmento'], prefix='segmento')
    kind_dummies = pd.get_dummies(df['kind'], prefix='kind')

    df = pd.concat([df, payment_place_dummies, segmento_dummies, kind_dummies], axis=1)
    df['result'] = df['status'].apply(lambda x: 1 if x == 'finished' else 0 if x == 'canceled' else None)
    df = df[df['status'].isin(['finished', 'canceled'])]

    return df

# Função para carregar os dados na tabela ia_duplicate_prediction
def load_data_to_db(df, connection):
    insert_query = """
    INSERT INTO ia_duplicate_prediction (
        score_entry_id, supplier_reference_id, installment, month_due_date, quarter_due_date,
        result, {payment_place_columns}, {segmento_columns}, {kind_columns}
    ) VALUES (%s, %s, %s, %s, %s, %s, {payment_place_values}, {segmento_values}, {kind_values})
    """

    payment_place_columns = ', '.join([f'payment_place_{col}' for col in df.columns if col.startswith('payment_place_')])
    segmento_columns = ', '.join([f'segmento_{col}' for col in df.columns if col.startswith('segmento_')])
    kind_columns = ', '.join([f'kind_{col}' for col in df.columns if col.startswith('kind_')])

    insert_query = insert_query.format(
        payment_place_columns=payment_place_columns,
        segmento_columns=segmento_columns,
        kind_columns=kind_columns,
        payment_place_values=', '.join(['%s'] * len(payment_place_columns.split(','))),
        segmento_values=', '.join(['%s'] * len(segmento_columns.split(','))),
        kind_values=', '.join(['%s'] * len(kind_columns.split(',')))
    )

    for _, row in df.iterrows():
        try:
            values = (
                row['id'], row['supplier_reference_id'], row['installment'], row['month_due_date'],
                row['quarter_due_date'], row['result']
            )

            payment_place_values = tuple(row[f'payment_place_{col}'] for col in payment_place_columns.split(', '))
            segmento_values = tuple(row[f'segmento_{col}'] for col in segmento_columns.split(', '))
            kind_values = tuple(row[f'kind_{col}'] for col in kind_columns.split(', '))
            all_values = values + payment_place_values + segmento_values + kind_values

            connection.execute_query(insert_query, all_values)
            logging.info(f"Inserção bem-sucedida para registro ID {row['id']}.")

        except Exception as e:
            logging.error(f"Falha ao inserir registro ID {row['id']}: {str(e)}")
            continue

# Função principal do ETL
def run_etl(input_file, endossantes_ids):
    df = pd.read_excel(input_file)
    transformed_df = transform_data(df, endossantes_ids)

    with PostgresConnection() as connection:
        load_data_to_db(transformed_df, connection)

    transformed_df.to_excel("arquivo_transformado.xlsx", index=False)

if __name__ == "__main__":
    input_file = 'C:\\Users\\Noite\\Desktop\\ProjetoIntegrador-SpcGrafeno-IA\\arquivo_original.xlsx'
    endossantes_ids = [123, 456, 789]  # Exemplo de IDs de endossantes
    run_etl(input_file, endossantes_ids)
