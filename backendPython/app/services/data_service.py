# app/services/data_service.py

import pandas as pd
from datetime import datetime
from collections import Counter
from ..repositories.database import PostgresConnection
from ..models.data_model import DataModel

class DataService:
    def __init__(self, db_params):
        self.db_params = db_params

    def process_data(self, file_path):
        base = pd.read_excel(file_path, sheet_name='Planilha1')

        datas = base['DAT PRAZO'].dropna().values
        data = {'DATA': list(Counter(datas).keys()), 'QTD': list(Counter(datas).values())}
        tabela_prazos = pd.DataFrame(data)

        date = pd.concat([base['DATE'], base['DAT PRAZO']], ignore_index=True)
        date = date.sort_values().unique().dropna()

        dicio = {}
        anterior = 0

        for d in date:
            dia = d.date()
            entrada = len(base[base['DATE'] == d])
            f_acumulado = len(base[base['DATE'] <= d])
            saida = int(tabela_prazos[tabela_prazos['DATA'] == str(dia)[:10]]['QTD'].sum())
            saida_acumulada = int(tabela_prazos[tabela_prazos['DATA'] <= d]['QTD'].sum())

            if str(d)[:10] == str(datetime.today())[:10]:
                resultado = f_acumulado
            else:
                resultado = f_acumulado - saida_acumulada

            data_model = DataModel(str(dia), anterior, entrada, f_acumulado, saida, saida_acumulada, resultado)
            dicio[str(dia)] = data_model
            anterior += entrada

        # Inserindo os dados no banco de dados
        self.insert_data(dicio)

        print(tabela_prazos)

    def insert_data(self, dicio):
        with PostgresConnection(**self.db_params) as db:
            for data in dicio.values():
                insert_query = """
                INSERT INTO resultados (DIA, SALDO_DIA_ANT, ENTRADA, TOTAL_ACUMULADO, SAIDA, SAIDA_ACUMULADA, RESULTADO)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                db.execute_query(insert_query, data.to_tuple())
