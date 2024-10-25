import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from unidecode import unidecode
import string
import joblib
from collections import Counter

class Transform:
    def __init__(self, file_path: str, file_type: str = 'csv', separator: str = ','):
        """
        Initializes the object with the original DataFrame.
        """
        self.df = self._load_file(file_path, file_type, separator)
        

    def _load_file(self, file_path: str, file_type: str, separator: str) -> pd.DataFrame:
        """
        Loads a file as a DataFrame based on the specified file type. 
        """
        if file_type.lower() == 'csv':
            return pd.read_csv(file_path, sep=separator, low_memory=False)
        elif file_type.lower() in ['txt', 'tsv']:
            return pd.read_csv(file_path, sep=separator, low_memory=False)
        else:
            raise ValueError("Tipo de arquivo não suportado. Utilize 'csv' ou 'txt'.")

    def rename_columns(self, columns_names: dict = None):
        """
        Rename specific columns on dataframe
        """
        self.df.rename(columns=columns_names, inplace=True)
        return self.df

    def select_useful_columns(self, columns: list):
        """
        Selects only the columns specified in the list
        """
        self.df = self.df[columns]
        return self.df
    
    def join_dataframe(self, other_df: pd.DataFrame,on: str, key:str, how: str = 'left', columns_to_select: list = None):
        """
        Executes the join between the current DataFrame and another DataFrame. 
        """
        if columns_to_select is not None:
            other_df = other_df[columns_to_select + [key]]
        # self.df = self.df.join(other_df.set_index(key), on=on, how=how)
        self.df = self.df.join(other_df.set_index(key), on=on, how=how)

        return self.df
    
    def get_data(self):
        """
        Retorna o DataFrame transformado.
        """
        return self.df

    def encode_categorical_columns(self, column:str):
        """
        Applies One-Hot Encoding to the selected categorical columns.
        It only transforms one column at a time
        """
        categorical_attributes = [column]
        categorical_columns = self.df[categorical_attributes]
        # Instance and train One Hot Encoder
        encoder = OneHotEncoder(handle_unknown='ignore')
        encoder.fit(categorical_columns)
        # Codify the categorical columns and transform in a dataframe
        encoded = encoder.transform(categorical_columns).toarray()

        encoded_column_names = encoder.get_feature_names_out(categorical_attributes)
        encoded_column_names = [name.split('_')[1] for name in encoded_column_names] 

        enc_train = pd.DataFrame(data = encoded, columns=encoded_column_names)
        self.df = pd.concat([self.df, enc_train], axis=1)
        self.df.drop(categorical_attributes, axis=1, inplace=True)

        return self.df

    def drop_columns(self, columns: list):
        """
        Remove useless columns
        """
        self.df.drop(columns, axis=1, inplace=True)
        return self.df
    
    def filter_not_equal(self, column, value):
        self.df = self.df[self.df[column] != value]
        return self.df
    
    def drop_na(self, column_name:str):
        """
        Remove rows with NaN in the specified columns
        """
        if column_name not in self.df.columns:
            raise ValueError(f"A coluna '{column_name}' não existe no DataFrame.")
        # Identificar as linhas com NaN na coluna especificada
        rows_with_nan = self.df[self.df[column_name].isna()].index
        # Remover essas linhas do DataFrame
        self.df.drop(rows_with_nan, inplace=True)
        # Agora remover colunas que ainda contenham NaN após remover as linhas
        self.df.dropna(axis=1, inplace=True)
        return self.df
    
    def extract_month(self, column_name: str):
        """
        Extract the month of the date
        """
        if column_name not in self.df.columns:
            raise ValueError(f"A coluna '{column_name}' não existe no DataFrame.")
        
        self.df[column_name] = pd.to_datetime(self.df[column_name])
        self.df['month'] = self.df[column_name].dt.month
        return self.df['month']
    
    def extract_quarter(self, column_name: str):
        """
        Extract quarter of the date
        """
        if column_name not in self.df.columns:
            raise ValueError(f"A coluna '{column_name}' não existe no DataFrame.")

        self.df[column_name] = pd.to_datetime(self.df[column_name], errors='coerce')
        self.df['quarter'] = self.df[column_name].dt.quarter
        return self.df['quarter']

    def replace_datetime_with_date(self, column_name: str):
        """
        Convert datetime columns for date (YYYY-MM-DD).
        """
        if column_name not in self.df.columns:
            raise ValueError(f"The column '{column_name}' does not exist in DataFrame.")        
        self.df[column_name] = pd.to_datetime(self.df[column_name], errors='coerce').dt.date
        return self.df[column_name]
    

    def subtract_dates(self, start_date_col: str, end_date_col: str, new_col_name: str):
        """
        Subtract two columns and creates a new column with result in month.
        """
        if start_date_col not in self.df.columns or end_date_col not in self.df.columns:
            raise ValueError(f"Uma das colunas '{start_date_col}' ou '{end_date_col}' não existe no DataFrame.")
        
        # Converter ambas as colunas para datetime, se necessário
        self.df[start_date_col] = pd.to_datetime(self.df[start_date_col], errors='coerce')
        self.df[end_date_col] = pd.to_datetime(self.df[end_date_col], errors='coerce')
        
        # Calcular a diferença em meses entre as datas
        def diff_in_months(start_date, end_date):
            if pd.isnull(start_date) or pd.isnull(end_date):
                return np.nan
            return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

        self.df[new_col_name] = self.df.apply(lambda row: diff_in_months(row[start_date_col], row[end_date_col]), axis=1)
        return self.df
    
    def to_uppercase(self, column_name: str):
        """
        Convert all the values to upper
        """
        if column_name not in self.df.columns:
            raise ValueError(f"The column '{column_name}' does not exist in DataFrame.")
        
        self.df[column_name] = self.df[column_name].str.upper()
        return self.df
    
    def remove_accent(self, column: str):
        self.df[column] = self.df[column].apply(unidecode)
        return self.df

    def set_locate(self, column:str):
        """
        set state
        """
        state_brazil = {
            "ACRE": "AC",
            "ALAGOAS": "AL",
            "AMAPÁ": "AP",
            "AMAPA": "AP",
            "AMAZONAS": "AM",
            "BAHIA": "BA",
            "CEARÁ": "CE",
            "CEARA": "CE",
            "DISTRITO FEDERAL": "DF",
            "ESPÍRITO SANTO": "ES",
            "ESPIRITO SANTO": "ES",
            "GOIÁS": "GO",
            "GOIAS": "GO",
            "MARANHÃO": "MA", 
            "MARANHAO": "MA", 
            "MATO GROSSO": "MT",
            "MATO GROSSO DO SUL": "MS",
            "MINAS GERAIS": "MG",
            "PARÁ": "PA",
            "PARA": "PA",
            "PARAÍBA": "PB",
            "PARAIBA": "PB",
            "PARANÁ": "PR",
            "PARANA": "PR",
            "PERNAMBUCO": "PE",
            "PIAUÍ": "PI",
            "PIAUI": "PI",
            "RIO DE JANEIRO": "RJ",
            "RIO GRANDE DO NORTE": "RN",
            "RIO GRANDE DO SUL": "RS",
            "RONDÔNIA": "RO",
            "RONDONIA": "RO",
            "RORAIMA": "RR",
            "SANTA CATARINA": "SC",
            "SÃO PAULO": "SP",
            "SAO PAULO": "SP",
            "SERGIPE": "SE",
            "TOCANTINS": "TO"
        }
        city_state_1 = {
            'RIACHAO': 'BA',
            'ICAPUI': 'CE',
            'LENCOIS PAULISTA': 'SP',
            'DIVINOPOLIS': 'MG',
            'SAO BERNARDO DO CAMPO': 'SP',
            'PAULINIA': 'SP',
            'ARAGUAINA': 'TO',
            'BRUSQUE': 'SC',
            'PAROBE': 'RS',
            'GUAXUPE': 'MG',
            'CRUZ MACHADO': 'PR',
            'APARECIDA DE GOIANIA': 'GO',
            'VALPARAISO': 'SP',
            'JARI': 'AP',
            'PARACATU': 'MG',
            'PORTO MAUA': 'MS',
            'DIVINOPOLIS': 'MG',
            'RINOPOLIS': 'SP',
            'HORTOLANDIA': 'SP',
            'PIRAJUI': 'SP',
            'GENERAL SALGADO': 'SP',
            'PALESTINA': 'SP',
            'MONTE AZUL PAULISTA': 'SP',
            'TUPA': 'SP',
            'DIADEMA': 'SP',
            'COTIA': 'SP',
            'ITAPECERICA DA SERRA': 'SP',
            'RIBEIRAO DO SUL': 'SP',
            'TEODORO SAMPAIO': 'SP',
            'ARARAS': 'SP',
            'EMBU DAS ARTES': 'SP',
            'MARABA PAULISTA': 'SP',
            'CASTILHO': 'SP',
            'AREALVA': 'SP',
            'REGENTE FEIJO': 'SP',
            'TAUBATE': 'SP',
            'PRESIDENTE VENCESLAU': 'SP',
            'CANAS': 'SP',
            'PANORAMA': 'SP',
            'VOTORANTIM': 'SP',
            'TAGUAI': 'SP',
            'ITAPEVI': 'SP',
            'PARAGUACU PAULISTA': 'SP',
            'SANTO ANDRE': 'SP',
            'ARUJA': 'SP',
            'FRANCO DA ROCHA': 'SP',
            'VARZEA PAULISTA': 'SP',
            'BARUERI': 'SP',
            'ITAQUAQUECETUBA': 'SP',
            'GOIATUBA': 'GO',
            'IBIUNA': 'SP',
            'CAMPOS DO JORDAO': 'SP',
            'POMPEIA': 'SP',
            'JUNDIAI': 'SP',
            'ADAMANTINA': 'SP',
            'PIRAJU': 'SP',
            'ENGENHEIRO COELHO': 'SP',
            'CASA BRANCA': 'SP',
            'MANDAGUACU': 'PR',
            'ARAPONGAS': 'PR',
            'MARINGA': 'PR',
            'TELEMACO BORBA': 'PR',
            'OSASCO': 'SP',
            'ABADIA DE GOIÁS': 'GO',
            'JUIZ DE FORA': 'MG',
            'SAPUCAIA DO SUL': 'RS',
            'CAPIVARI': 'SP',
            'GUARULHOS': 'SP',
            'PELOTAS': 'RS',
            'JAGUARIUNA': 'SP',
            'CAMPINAS': 'SP',
            'BELO HORIZONTE': 'MG',
            'CURITIBA': 'PR',
            'MOGI DAS CRUZES': 'SP',
            'SOROCABA': 'SP',
            'ITUIUTABA': 'MG',
            'ANÁPOLIS': 'GO',
            'FRANCA': 'SP',
            'VALPARAÍSO': 'GO',
            'SAO CARLOS': 'SP',
            'ITAPOLIS': 'SP',
            'BARRETOS': 'SP',
            'ABADIA DE GOIAS': 'GO',
            'LEME': 'SP',
            'UBERLANDIA': 'MG',
            'CAPANEMA': 'PR',
            'CAIEIRAS': 'SP',
            'GOIANIA': 'GO',
            'JARDINOPOLIS': 'SP',
            'SAO FRANCISCO DO PARA': 'PA',
            'ANAPOLIS': 'GO',
            'BAURU': 'SP',
            'PORTO ALEGRE': 'RS',
            'SAO JOAO DA BOA VISTA': 'SP',
            'PATROCINIO': 'MG',
            'SERRINHA': 'BA',
            'OLIMPIA': 'SP',
            'PRESIDENTE PRUDENTE': 'SP',
            'SAO JOSE DO RIO PRETO': 'SP',
            'CAMPOS NOVOS PAULISTA': 'SP',
            'CARAPICUIBA': 'SP',
            'SANTA ROSA DE VITERBO': 'SP',
            'ABADIANIA': 'GO',
            'ABADIA DOS DOURADOS': 'MG',
            'ABAETETUBA': 'PA',
            'MARTINOPOLIS': 'SP'
        }
        self.df[column] = self.df[column].apply(lambda l: l.split('/')[1] if len(l.split('/')) > 1 else l)
        self.df[column] = self.df[column].apply(lambda l: l.split('-')[0] if len(l.split('-')) > 1 else l)
        self.df[column] = self.df[column].apply(lambda l: l.split(',')[1] if len(l.split(',')) > 1 else l)
        self.df[column] = self.df[column].apply(lambda x: state_brazil.get(x, x))
        self.df[column] = self.df[column].apply(lambda x: city_state_1.get(x, x))

        return self.df
    
    def remove_spaces(self, column):
        """ Remove blank space"""
        self.df[column] = self.df[column].str.strip()
        return self.df
    
    def drop_not_state(self, column):
        """
            Remove text with more than 2 characters
        """
        self.df = self.df[self.df[column].apply(lambda x: len(str(x)) <= 2)]
        return self.df
        
    def reset_dataframe_index(self):
        """ Reset the indexes of the dataframe"""
        self.df = self.df.reset_index(drop=True)
        return self.df
    
    def remove_punctuations(self, column: str):
        """Removes punctuation from the specified column of the DataFrame using string.punctuation."""
        # Creates a translation table to remove punctuation characters
        removal_table  = str.maketrans('', '', string.punctuation)

        # Aplica a tabela de tradução à coluna do DataFrame
        self.df[column] = self.df[column].apply(lambda texto: texto.translate(removal_table))
        return self.df

    def create_sectors_industry_columns(self, column:str, words:list):
        """Creates a new column in the DataFrame for each word in the list,
        filled with 1 if the word is found in the specified column, otherwise 0."""
        self.df['OUTROS'] = 0
        for word in words:
            # Create a new column with the name of the word, checking if it exists in the specified column
            self.df[word] = self.df[column].apply(lambda x: 1 if word in str(x) else 0)
        # Update 'Others' column where none of the words are found
        self.df['OUTROS'] = self.df[['OUTROS'] + words].sum(axis=1).apply(lambda x: 1 if x == 0 else 0)
        return self.df

    def save_dataframe_to_pickle(self, filename:str):
        """Saves the given DataFrame to a pickle file using joblib."""
        try:
            joblib.dump(self.df, filename)
            print(f"DataFrame saved to {filename}")
        except Exception as e:
            print(f"An error occurred while saving the DataFrame: {e}")

if __name__ == "__main__":
    # Define file_path, type and separator
    file_path = 'C:\\Users\\Noite\\Downloads\\spcgrafeno\\asset_trade_bills.csv'
    file_type = 'csv'
    separator = ','
    # Instantiate the transformer and load the DataFrame from the specified file
    base_duplicates = Transform(file_path, file_type, separator)
    df_duplicates = base_duplicates.get_data()
    # Rename some columns
    columns_to_rename = {
        df_duplicates.iloc[:,8].name: 'expiration_date',
        df_duplicates.iloc[:,15].name: 'locate',
        df_duplicates.iloc[:,9].name: 'start_date',
        df_duplicates.iloc[:,4].name: 'segment',
        df_duplicates.iloc[:,5].name: 'status',
        df_duplicates.iloc[:,7].name: 'supplier_id',
        }
    base_duplicates.rename_columns(columns_to_rename)
    # Select useful columns
    selected_columns = ['expiration_date', 'locate', 'start_date', 'segment', 'status', 'supplier_id']
    base_duplicates.select_useful_columns(selected_columns)

    # Define file_path, type and separator
    file_path = 'C:\\Users\\Noite\\Downloads\\spcgrafeno\\asset_parts.csv'
    # Instantiate the transformer and load the DataFrame from the specified file
    auxiliar_base = Transform(file_path, file_type, separator)
    df_auxiliar = auxiliar_base.get_data()
    # Rename some columns
    columns_to_rename = {
        df_auxiliar.iloc[:,0].name: 'key',
        df_auxiliar.iloc[:,1].name: 'supplier_name'
        }
    auxiliar_base.rename_columns(columns_to_rename)
    # Select useful columns
    selected_columns = ['key', 'supplier_name']
    auxiliar_base.select_useful_columns(selected_columns)
    # Join supplier name in the first dataframe
    key_on = 'supplier_id'
    key_other_df = 'key'
    join_type = 'left'
    columns_to_bring = ['supplier_name']
    base_duplicates.join_dataframe(
        other_df = auxiliar_base.get_data(),
        on = key_on,
        key = key_other_df,
        how = join_type,
        columns_to_select = columns_to_bring)
    # ONE-HOT-ENCODING
    # It only transforms one column at a time
    # encoding segment's column
    base_duplicates.encode_categorical_columns(column='segment')
    # Drop useless columns
    columns_to_drop = ['supplier_id']
    base_duplicates.drop_columns(columns=columns_to_drop)    
    # Filtering duplicates not equal acive
    base_duplicates.encode_categorical_columns('status')

    df_duplicates = base_duplicates.get_data()

    # columns_to_rename = {
    #     df_duplicates.iloc[:,4].name: 'goods',
    #     df_duplicates.iloc[:,5].name: 'services',
    #     df_duplicates.iloc[:,6].name: 'active',
    #     df_duplicates.iloc[:,7].name: 'canceled',
    #     df_duplicates.iloc[:,8].name: 'finished',
    # }
    # base_duplicates.rename_columns(columns_to_rename)
    base_duplicates.drop_na('supplier_name')
    # Filter not active
    # base_duplicates.get_data()
    base_duplicates.filter_not_equal('active', 1.0)
    # Drop useless columns
    columns_to_drop = ['active']
    base_duplicates.drop_columns(columns=columns_to_drop)    
    # Extract month of the year
    base_duplicates.extract_month('expiration_date')
    # Extract quarter of the year
    base_duplicates.extract_quarter('expiration_date')
    # Remove time
    base_duplicates.replace_datetime_with_date('start_date')
    # Create installment
    base_duplicates.subtract_dates('start_date', 'expiration_date', 'installment')
    # Drop useless columns
    columns_to_drop = ['expiration_date', 'start_date']
    base_duplicates.drop_columns(columns_to_drop)
    # Remove null data
    base_duplicates.drop_na('locate')
    # Transform locate values
    base_duplicates.to_uppercase('locate')
    base_duplicates.remove_accent('locate')
    # Define states
    base_duplicates.set_locate('locate')
    base_duplicates.remove_spaces('locate')
    # Remove useless data
    base_duplicates.drop_not_state('locate')
    # Encode 
    
    # print(base_duplicates.get_data())
    base_duplicates.reset_dataframe_index()
    base_duplicates.encode_categorical_columns('locate')
    # print(base_duplicates.get_data())

    supplier_name = base_duplicates.get_data()['supplier_name']
    supplier_name = supplier_name.sort_values().drop_duplicates().str.upper()
    text = ' '.join(supplier_name)
    text = text.translate(str.maketrans('', '', string.punctuation))
    words = text.split()
    cont = Counter(words)
    
    for word, frequency in cont.most_common():
        print(f"{word}")
    print(len(cont))

    industry_sector = ['COMERCIO', 'INDUSTRIA', 'DISTRIBUIDORA', 'PRODUTOS', 'PLASTICOS', 'QUIMICA', 'SERVICOS', 'ALIMENTOS', 'METAIS', 'EMBALAGENS', 'TEXTIL', 'ELETRONICO', 'ELETRICOS', 'AGRICOLAS', 'MEDICAMENTOS', 'FRIGORIFICO', 'PECAS', 'LOGISTICA', 'COMPONENTES', 'AGROPECUARIA', 'TRADING', 'BEBIDAS', 'SUPRIMENTOS', 'TRANSPORTE', 'SIDERURGICOS', 'FARMACIA', 'DIAGNOSTICOS', 'CONSTRUCOES', 'CONSULTORIA', 'FINANCEIRA', 'ARGAMASSA', 'FABRICAN', 'PETROLEO', 'TERMOPLASTICOS', 'METALURGICOS', 'SUPLEMENTOS', 'FUNDICAO', 'VEICULOS', 'EQUIPAMENTOS']
    base_duplicates.to_uppercase('supplier_name')
    base_duplicates.remove_accent('supplier_name')
    base_duplicates.remove_punctuations('supplier_name')
    base_duplicates.create_sectors_industry_columns('supplier_name', industry_sector)
    base_duplicates.drop_columns(['supplier_name'])
    base_duplicates.save_dataframe_to_pickle('dataframe.pkl')
    df = base_duplicates.get_data()
    