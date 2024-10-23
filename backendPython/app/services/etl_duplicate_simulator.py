import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder


class Transform:
    def __init__(self, file_path: str, file_type: str = 'csv', separator: str = ','):
        """
        Initializes the object with the original DataFrame.
        """
        self.df = self._load_file(file_path, file_type, separator)
        self.encoder = OneHotEncoder(handle_unknown='ignore')

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

    def encode_categorical_columns(self, column:list):
        """
        Applies One-Hot Encoding to the selected categorical columns.
        It only transforms one column at a time
        """
        self.encoder.fit(self.df[column])
        encoded_df = self.encoder.transform(self.df[column]).toarray()
        enc_train = pd.DataFrame(encoded_df, columns=self.encoder.categories_)
        self.df = pd.concat([self.df, enc_train], axis=1)
        self.df.drop(column, axis=1, inplace=True)

        return self.df

    def drop_columns(self, columns: list):
        """
        Remove useless columns
        """
        self.df.drop(columns, axis=1, inplace=True)
        return self.df
    
if __name__ == "__main__":
    # Define file_path, type and separator
    file_path = 'C:\\Developer\\duplicates_table.csv'  
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
    file_path = 'C:\\Developer\\supplier_table.csv'  
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
    column_to_encode = ['segment']
    base_duplicates.encode_categorical_columns(column=column_to_encode)
    # encoding status' column
    column_to_encode = ['status']
    base_duplicates.encode_categorical_columns(column=column_to_encode)
    # Drop useless columns
    columns_to_drop = ['supplier_id']
    base_duplicates.drop_columns(columns=columns_to_drop)
    base_final = base_duplicates.get_data().head()
    print(base_final['start_date'].astype)