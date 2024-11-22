import pandas as pd
import logging
from app.repositories.database import PostgresConnection
import uuid

# Configuração de logs
logging.basicConfig(
    filename="insercao_dados.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def carregar_asset_parts(asset_parts_path):
    """
    Lê a tabela `asset_parts` e retorna um dicionário mapeando `id` para `name`.
    """
    try:
        df_parts = pd.read_csv(asset_parts_path, low_memory=False, sep=";")
        if 'id' not in df_parts.columns or 'name' not in df_parts.columns:
            raise KeyError("As colunas 'id' e 'name' são obrigatórias em asset_parts.")
        return df_parts.set_index('id')['name'].to_dict()
    except Exception as e:
        logging.error(f"Erro ao carregar asset_parts: {e}")
        raise

def adicionar_segmento(df_bills, asset_parts_map):
    """
    Adiciona a coluna `segmento` ao DataFrame `df_bills` com base no `asset_parts_map`.
    """
    def classificar_segmento(asset_part_id):
        name = asset_parts_map.get(asset_part_id, "").lower()
        if any(word in name for word in ["stg", "fidc", "investimento", "investimentos", "fgts", "finan", "invest", "credito"]):
            return "Fundo"
        elif "teste" in name:
            return "Outros"
        return "Comércio"
    
    if 'endorser_original_id' not in df_bills.columns:
        raise KeyError("A coluna 'endorser_original_id' está ausente no arquivo trade_bills.")
    
    df_bills['segmento'] = df_bills['endorser_original_id'].apply(classificar_segmento)
    return df_bills

def adicionar_colunas_payment_place(df_bills):
    """
    Adiciona as colunas de "payment_place" no formato One-Hot Encoding.
    """
    estados = ['SP', 'RJ', 'MG', 'RS']
    for estado in estados:
        coluna = f'payment_place_{estado.lower()}'
        df_bills[coluna] = df_bills['payment_place'].str.upper().fillna("").apply(lambda x: estado in x)
    return df_bills

def adicionar_colunas_segmento(df_bills):
    """
    Adiciona as colunas de segmento no formato One-Hot Encoding.
    """
    segmentos = ['Financial', 'Commercial', 'Industrial', 'Educational']
    for segmento in segmentos:
        coluna = f'segment_{segmento.lower()}'
        df_bills[coluna] = df_bills['segmento'].str.capitalize().fillna("").apply(lambda x: segmento in x)
    return df_bills

def adicionar_colunas_kind(df_bills):
    """
    Adiciona as colunas de "kind" no formato One-Hot Encoding.
    """
    tipos = ['Receivable', 'Invoice', 'Check']
    for tipo in tipos:
        coluna = f'kind_{tipo.lower()}'
        df_bills[coluna] = df_bills['kind'].str.capitalize().fillna("").apply(lambda x: tipo in x)
    return df_bills

def load_data_to_db(df, connection):
    """
    Insere os dados transformados diretamente no banco.
    """
    insert_query = """
    INSERT INTO ia_duplicate_prediction (
        id, installment, month_due_date, quarter_due_date,
        payment_place_sp, payment_place_rj, payment_place_mg, payment_place_rs,
        segment_financial, segment_commercial, segment_industrial, segment_educational,
        kind_receivable, kind_invoice, kind_check, result
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    for _, row in df.iterrows():
        try:
            values = (
                str(uuid.uuid4()),  # Gera ID único
                row['installment'], 
                row['month_due_date'], 
                row['quarter_due_date'],
                row['payment_place_sp'], 
                row['payment_place_rj'], 
                row['payment_place_mg'], 
                row['payment_place_rs'],
                row['segment_financial'], 
                row['segment_commercial'], 
                row['segment_industrial'], 
                row['segment_educational'],
                row['kind_receivable'], 
                row['kind_invoice'], 
                row['kind_check'], 
                row['result']
            )
            connection.execute_query(insert_query, values)
            logging.info(f"Inserção bem-sucedida para registro ID {row['id']}.")
        except Exception as e:
            logging.error(f"Erro ao inserir registro ID {row['id']}: {str(e)}")

def run_etl_and_insert(asset_parts_path, asset_trade_bills_path):
    """
    Executa o ETL e insere os dados no banco diretamente.
    """
    try:
        # Carrega a tabela asset_parts como um dicionário
        asset_parts_map = carregar_asset_parts(asset_parts_path)
        
        # Lê a tabela trade_bills
        df_bills = pd.read_csv(asset_trade_bills_path, low_memory=False, sep=";")
        
        # Adiciona a coluna segmento
        df_bills = adicionar_segmento(df_bills, asset_parts_map)
        
        # Adiciona colunas adicionais (One-Hot Encodings)
        df_bills = adicionar_colunas_payment_place(df_bills)
        df_bills = adicionar_colunas_segmento(df_bills)
        df_bills = adicionar_colunas_kind(df_bills)

        # Realiza mais transformações
        df_bills['due_date'] = pd.to_datetime(df_bills['due_date'], format="%Y-%m-%d", errors='coerce')
        df_bills['created_at'] = pd.to_datetime(df_bills['created_at'], format="%Y-%m-%d", errors='coerce')
        
        df_bills['installment'] = ((df_bills['due_date'] - df_bills['created_at']).dt.days / 30).fillna(0).astype(int)
        df_bills['month_due_date'] = df_bills['due_date'].dt.month.fillna(0).astype(int)
        df_bills['quarter_due_date'] = df_bills['due_date'].dt.quarter.fillna(0).astype(int)
        
        df_bills['result'] = df_bills['state'].apply(lambda x: 1 if x == 'finished' else 0 if x == 'canceled' else None).fillna(0).astype(int)

        # Insere os dados no banco
        with PostgresConnection() as connection:
            load_data_to_db(df_bills, connection)
        
        logging.info("Processo ETL e inserção concluídos com sucesso.")
    except Exception as e:
        logging.error(f"Erro no processo ETL: {str(e)}")
        raise

if __name__ == "__main__":
    # Caminhos para os arquivos de entrada
    asset_parts_path = 'C:\\Users\\Noite\\Desktop\\API\\bases_dados\\asset_parts.csv'
    asset_trade_bills_path = 'C:\\Users\\Noite\\Desktop\\API\\bases_dados\\asset_trade_bills.csv'
    
    # Executa o processo
    run_etl_and_insert(asset_parts_path, asset_trade_bills_path)
