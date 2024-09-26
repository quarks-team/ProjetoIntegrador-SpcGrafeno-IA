import pandas as pd

# ETL da Tabela asset_parts
def etl_asset_parts(file_path):
    # Extract: Carregar os dados
    df_asset_parts = pd.read_csv(file_path)

    # Transform: Limpar e transformar os dados
    df_asset_parts.drop_duplicates(inplace=True)  # Remover duplicatas
    df_asset_parts.fillna('', inplace=True)  # Preencher valores nulos com string vazia
    
    # Padronizar os dados de 'type' para facilitar o filtro
    df_asset_parts['type'] = df_asset_parts['type'].str.lower()

    return df_asset_parts

# Função para detectar segmentos dentro de asset_parts
def detectar_segmentos_asset_parts(df_asset_parts, endossantes_ids):
    segmentos = []

    for idx, row in df_asset_parts.iterrows():
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
    
    df_asset_parts['segmento'] = segmentos
    return df_asset_parts

# Carregar os dados de participants (para referência)
df_participants = pd.read_csv('C:\\Users\\Noite\\Desktop\\API\\dataset\\participants.csv')

# Executar o ETL para asset_parts
df_asset_parts = etl_asset_parts('C:\\Users\\Noite\\Desktop\\API\\dataset\\asset_parts.csv')

# Carregar os dados de asset_trade_bills
df_trade_bills = pd.read_csv('C:\\Users\\Noite\\Desktop\\API\\dataset\\asset_trade_bills.csv')

# Identificar endossantes na tabela asset_parts
endossantes_parts = df_asset_parts[df_asset_parts['type'] == 'assetendorser']['id'].unique()

# Identificar endossantes na tabela asset_trade_bills
endossantes_trade_bills = df_trade_bills['endorser_original_id'].dropna().unique()

# Combinar os IDs de endossantes das duas tabelas
todos_endossantes = set(endossantes_parts).union(set(endossantes_trade_bills))

# Aplicar a função de detecção de segmentos diretamente em asset_parts
df_asset_parts_com_segmentos = detectar_segmentos_asset_parts(df_asset_parts, todos_endossantes)

# Visualizar o DataFrame transformado com a nova coluna de segmentos
print(df_asset_parts_com_segmentos[['name', 'segmento']])

# Salvar o DataFrame transformado em um novo arquivo CSV
df_asset_parts_com_segmentos.to_csv('asset_parts_transformado_com_segmentos.csv', index=False)
