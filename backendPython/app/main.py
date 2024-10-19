# app/main.py

from fastapi import FastAPI
from app.config import DatabaseConfig
from app.services.ia_model import InputData,model,scaler,base_with_names
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from datetime import date

app = FastAPI()

db_params = DatabaseConfig.get_params()

@app.on_event("startup")
async def startup_event():
    # Aqui você pode fazer inicializações se necessário
    print("FastAPI is starting up...")

@app.get("/")
async def root():
    """Endpoint raiz."""
    return {"message": "API está funcionando. Acesse /docs para ver a documentação."}

@app.post("/predict-score/")
async def predict(nome, data: InputData):
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
    score = model.predict(X_scaled)
    return int(score[0]),data

@app.get("/test-for/")
async def for_test():
    list_endorser = []
    for n, i in base_with_names.iterrows():
        # print(base_with_names.iloc[[n]])
        data = {
            'renegotiation_delay_days' : 0,
            'segment_products_count' : 0,
            'segment_services_count' : 0,
            'ongoing_transactions' : 0,
            'voided_transactions' : 0,
            'successful_transactions' : 0,
            'non_voided_transactions' : 0,
            'median_installment_amount' : 0,
            'overall_transactions' : 0
        }
        list_endorser.append([i['NOME_ENDOSSER'], predict(i['NOME_ENDOSSER'], data)])
    return list_endorser