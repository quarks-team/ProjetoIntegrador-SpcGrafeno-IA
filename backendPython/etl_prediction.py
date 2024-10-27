import pandas as pd
from datetime import datetime
from app.repositories.database import PostgresConnection

# Função para detectar segmentos dentro dos dados de duplicatas
def detectar_segmentos(df, endossantes_ids):
    segmentos = []

    for idx, row in df.iterrows():
        nome_lower = str(row['name']).lower()  # Padronizar para minúsculas
        
        # Verificar se o item é endossante
        if row['id'] in endossantes_ids:
            segmentos.append("Endossante")
        # Caso não seja endossante, verificar as palavras-chave para "Fundo"
        elif any(word in nome_lower for word in ["stg", "fidc", "investimento", "investimentos", "fgts", "finan", "invest", "credito"]):
            segmentos.append("Fundo")
        # Caso o nome tenha "teste", classificar como "Outros"
        elif "teste" in nome_lower:
            segmentos.append("Outros")
        # Se não corresponder a nenhum dos critérios anteriores, classificar como "Comércio"
        else:
            segmentos.append("Comércio")
    
    df['segmento'] = segmentos
    return df

# Função para transformar os dados
def transform_data(df, endossantes_ids):
    # Detectar segmentos
    df = detectar_segmentos(df, endossantes_ids)
    
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
    # Ajustar a query de inserção com base nos dummies gerados
    insert_query = """
    INSERT INTO ia_score_data (
        score_entry_id, supplier_reference_id, installment, month_due_date, quarter_due_date,
        result, {payment_place_columns}, {segmento_columns}, {kind_columns}
    ) VALUES (%s, %s, %s, %s, %s, %s, {payment_place_values}, {segmento_values}, {kind_values})
    """
    
    # Extrair as colunas dinâmicas geradas pelo One-Hot Encoding
    payment_place_columns = ', '.join([f'payment_place_{col}' for col in df.columns if col.startswith('payment_place_')])
    segmento_columns = ', '.join([f'segmento_{col}' for col in df.columns if col.startswith('segmento_')])
    kind_columns = ', '.join([f'kind_{col}' for col in df.columns if col.startswith('kind_')])

    # Adaptar o query para incluir esses valores
    insert_query = insert_query.format(
        payment_place_columns=payment_place_columns,
        segmento_columns=segmento_columns,
        kind_columns=kind_columns,
        payment_place_values=', '.join(['%s'] * len(payment_place_columns.split(','))),
        segmento_values=', '.join(['%s'] * len(segmento_columns.split(','))),
        kind_values=', '.join(['%s'] * len(kind_columns.split(',')))
    )

    for _, row in df.iterrows():
        values = (
            row['id'], row['supplier_reference_id'], row['installment'], row['month_due_date'],
            row['quarter_due_date'], row['result']
        )
        
        # Adicionar os valores de One-Hot Encoding das colunas dinâmicas
        payment_place_values = tuple(row[f'payment_place_{col}'] for col in payment_place_columns.split(', '))
        segmento_values = tuple(row[f'segmento_{col}'] for col in segmento_columns.split(', '))
        kind_values = tuple(row[f'kind_{col}'] for col in kind_columns.split(', '))
        
        all_values = values + payment_place_values + segmento_values + kind_values
        connection.execute_query(insert_query, all_values)

# Função principal do ETL
def run_etl(input_file, endossantes_ids):
    # Carregar os dados
    df = pd.read_excel(input_file)

    # Transformar os dados
    transformed_df = transform_data(df, endossantes_ids)

    # Conectar ao banco e carregar os dados transformados
    with PostgresConnection() as connection:
        load_data_to_db(transformed_df, connection)

# Executar o ETL com o arquivo de entrada
if __name__ == "__main__":
    input_file = 'C:\\Users\\Noite\\Desktop\\ProjetoIntegrador-SpcGrafeno-IA\\asset_trade_bills_transformada.xlsx'
    
    # Definir os IDs de endossantes (pode ser carregado de outra fonte ou calculado anteriormente)
    endossantes_ids = [123, 456, 789]  # Exemplo de IDs de endossantes
    
    run_etl(input_file, endossantes_ids)
