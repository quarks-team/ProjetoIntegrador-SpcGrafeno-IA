# app/main.py

from fastapi import FastAPI, File, UploadFile, HTTPException  # Adicionar 'File' aqui
# from app.config import DatabaseConfig
from app.services.ia_model import InputData,model,scaler,base_with_names
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from datetime import date
import datetime
import logging
import json
from app.repositories.database import PostgresConnection
import os
from dotenv import load_dotenv
from app.config import DatabaseConfig
import pandas as pd
from io import BytesIO
import logging

from app.services.user_service import UserService  # Serviço de inserção de usuários no banco

db_x = DatabaseConfig()

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



app = FastAPI()
if __name__ == '__main__':
    # Obtém os parâmetros do banco de dados do arquivo .env
    db_params = DatabaseConfig.get_params()
# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    # Aqui você pode fazer inicializações se necessário
    print("FastAPI is starting up...")

@app.get("/")
async def root():
    """Endpoint raiz."""
    return {"message": "API está funcionando. Acesse /docs para ver a documentação."}

def preprocess_data(data:InputData):
    """ 
    Transforms the input data into a scaled numpy array suitable for prediction. 
    """
    variables = [
        data.renegotiation_delay_days, 
        data.segment_products_count,
        data.segment_services_count,
        data.ongoing_transactions, 
        data.voided_transactions, 
        data.successful_transactions, 
        data.non_voided_transactions,
        data.median_installment_amount,
        data.overall_transactions
        ]
    X = np.array(variables).reshape(1, -1)
    X_scaled = scaler.transform(X)
    return X_scaled

@app.post("/predict-score/")
async def predict(name: str, data: InputData):
    """
    Predicts the score based on endorser input data
    """
    try:
        logger.info(f"Predicting score for endorser: {name}")
        # Preprocess    
        X_scaled = preprocess_data(data)
        # Predicting score
        score = model.predict(X_scaled)
       
        return {    
            'final_score': int(score[0]),
            'input_variables': data,
            'endorser_name': name,
            'created_timestamp': datetime.datetime.now().isoformat()            
            }
    except Exception as e:
        logger.error(f"Error in predicting score: {str(e)}")
        raise HTTPException(status_code=500, detail="Error in processing the prediction.")

@app.get("/score-result/")
async def get_all_score_result():
    """
    Fetches the score for all endorsers
    """
    list_endorser = []
    try:
        for n, i in base_with_names.iterrows():        
            endorser_data  = InputData(
            renegotiation_delay_days = i.iloc[1],
            segment_products_count = i.iloc[2],
            segment_services_count = i.iloc[3],
            ongoing_transactions = i.iloc[4],
            voided_transactions = i.iloc[5],
            successful_transactions = i.iloc[6],
            non_voided_transactions = i.iloc[7],
            median_installment_amount = i.iloc[8],
            overall_transactions = i.iloc[9]
            )
            result = await predict(i.iloc[0], endorser_data)
            list_endorser.append(result)
        return list_endorser
    except Exception as e:
        logger.error(f"Error in fetching all scores: {str(e)}")
        raise HTTPException(status_code=500, detail="Error in retrieving scores.")

@app.get("/insert-data")
async def insert_data():
    
    """
    Insert data in table
    """
    sql = """
    INSERT INTO public.ai_score_results(final_score, input_variables, endorser_name) VALUES (%s,%s,%s);
    """
    data = await get_all_score_result()
    with PostgresConnection() as db:
        for d in data:  
            dict_endoser  = {
            'renegotiation_delay_days' : d['input_variables'].renegotiation_delay_days,
            'segment_products_count' : d['input_variables'].segment_products_count,
            'segment_services_count' : d['input_variables'].segment_services_count,
            'ongoing_transactions' : d['input_variables'].ongoing_transactions,
            'voided_transactions' : d['input_variables'].voided_transactions,
            'successful_transactions' : d['input_variables'].successful_transactions,
            'non_voided_transactions' : d['input_variables'].non_voided_transactions,
            'median_installment_amount' : d['input_variables'].non_voided_transactions,
            'overall_transactions' : d['input_variables'].overall_transactions
            }
            
            try:
                final_score = d['final_score']
                input_variables = json.dumps(dict_endoser)
                endorser_name = str(d['endorser_name'])
                db.execute_query(sql, (final_score, input_variables, endorser_name))
                logger.info(f"Successfully inserted record for endorser: {endorser_name}")
                c+=1
                print(c)
            except Exception as e:
                logger.error(f'Error inserting record for endorser {d['endorser_name']}')
            
    return data


@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    """
    Endpoint que recebe o arquivo CSV e insere os dados no banco de dados.
    """
    if not file.filename.endswith("participants.csv"):
        raise HTTPException(status_code=400, detail="Arquivo não é um CSV")

    try:
        # Ler o conteúdo do arquivo CSV usando pandas
        content = await file.read()
        data = pd.read_csv(BytesIO(content))

        # Inserir os dados no banco de dados
        UserService.insert_users_from_dataframe(data)

        return {"detail": f"{file.filename} processado com sucesso."}
    except Exception as e:
        logger.error(f"Erro ao processar o arquivo CSV: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar o arquivo CSV")