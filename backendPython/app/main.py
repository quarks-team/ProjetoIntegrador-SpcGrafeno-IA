# app/main.py

from fastapi import FastAPI, HTTPException,Body, UploadFile
# from app.config import DatabaseConfig
from app.services.ia_model import InputData,model,scaler,base_with_names
from app.services.ia_duplicate_sumilator import model_simulator,scaler_simulator,DuplicateSimulator
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from datetime import date
from datetime import datetime as dt
import datetime
import logging
import json
from app.repositories.database import PostgresConnection
import os
from dotenv import load_dotenv
from app.config import DatabaseConfig
import pandas as pd
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import prophet
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
db_x = DatabaseConfig()



app = FastAPI()
# Configure o CORS
origins = [
    "http://localhost:9090",
    "http://127.0.0.1:9090"  # URL do seu frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # permite todos os métodos
    allow_headers=["*"],  # permite todos os cabeçalhos
)
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


@app.post('/predict-duplicate/')
async def predict_duplicate(data:DuplicateSimulator):
    # info: DuplicateSimulator
    """
    Teste
    """
    # Criar o DataFrame de entrada com base nos parâmetros
    input_data = pd.DataFrame(0, index=range(1), columns=[
        'goods', 'services', 'month', 'quarter', 'installment', 'AL', 'AM', 'AP',
        'BA', 'CE', 'ES', 'GO', 'MG', 'MS', 'PA', 'PI', 'PR', 'RJ', 'RS', 'SC',
        'SE', 'SP', 'TO', 'OUTROS', 'COMERCIO', 'INDUSTRIA', 'DISTRIBUIDORA',
        'PRODUTOS', 'PLASTICOS', 'QUIMICA', 'SERVICOS', 'ALIMENTOS', 'METAIS',
        'EMBALAGENS', 'TEXTIL', 'ELETRONICO', 'ELETRICOS', 'AGRICOLAS',
        'MEDICAMENTOS', 'FRIGORIFICO', 'PECAS', 'LOGISTICA', 'COMPONENTES',
        'AGROPECUARIA', 'TRADING', 'BEBIDAS', 'SUPRIMENTOS', 'TRANSPORTE',
        'SIDERURGICOS', 'FARMACIA', 'DIAGNOSTICOS', 'CONSTRUCOES', 'CONSULTORIA',
        'FINANCEIRA', 'ARGAMASSA', 'FABRICAN', 'PETROLEO', 'TERMOPLASTICOS',
        'METALURGICOS', 'SUPLEMENTOS', 'FUNDICAO', 'VEICULOS', 'EQUIPAMENTOS'
    ])
    
    if data.segment == 'goods':
        input_data['goods'] = 1
    elif data.segment == 'services':
        input_data['services'] = 1
    else:
        print("erro")
    input_data['month'] = data.month
    input_data['quarter'] = data.quarter
    for s in input_data.iloc[:,5:23].columns:
        if data.state == str(s):
            input_data[f'{s}'] = 1
    for a in data.area:
        for c in input_data.iloc[:,23:63].columns:
            if a == str(c):
                input_data[f'{c}'] = 1
    
    created_date = dt.strptime(data.created_date, "%d/%m/%Y")
    finalization_date = dt.strptime(data.date, "%d/%m/%Y")
    difference = finalization_date - created_date
    input_data['installment'] = difference.days
    columns_to_scale = ['installment','quarter', 'month']
    input_data[columns_to_scale] = scaler_simulator.fit_transform(input_data[columns_to_scale])
    result_duplicate = model_simulator.predict(input_data)
    proba = model_simulator.predict_proba(input_data)
    print(result_duplicate)
    print(proba)
    result_duplicate = result_duplicate[0]
    # if result_duplicate == 0:
    #     proba = round(proba[0][0], 2)
    # else:
    proba = round(proba[0][1], 2)

    print(result_duplicate)
    print(proba)
    return { 
        "probability": proba
        }
    
@app.post('/upload-csv/')
async def upload_data(file: UploadFile(...), type_duplicates:str, predict_days: int):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="The file must be a csv.")
    try:
        df = pd.read_csv(file.file,sep=',', low_memory=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error to process the file: {str(e)}")

    match type_duplicates:
        case 'active':
            active = df[df[df.iloc[:,5].name] == 'active']
            active = prepare_df(active)
            active = prepare_df(active,'01/01/2024','30/03/2025')
            active = prepare_data_prophet(active)
            steps = 50
            data_train = prepare_data_train(active, steps)
            data_test = prepare_data_test(active, steps)
            model = train_model(data_train)
            forecast = predict(model, predict_days, 'D') 
            return forecast
            
        case 'finished':
            finished = df[df[df.iloc[:,5].name] == 'finished']
            finished = prepare_df(finished)
            finished = filter_data_df(finished,'01/01/2024','11/11/2024')
            finished = prepare_data_prophet(finished)
            steps = 89
            data_train = prepare_data_train(finished, steps)
            data_test = prepare_data_test(finished, steps)
            model = train_model(data_train)
            forecast = predict(model, predict_days, 'D') 
            return forecast
        case 'canceled':
            canceled = df[(df[df.iloc[:,10].name].notna()) & (df['state'] == 'canceled')]
            canceled = canceled[(canceled[canceled.iloc[:,10].name].notna()) & (canceled['state'] == 'canceled')]
            canceled[canceled.iloc[:,10].name] = canceled[canceled.iloc[:,10].name].str.slice(0,10)
            canceled = canceled.groupby(canceled.iloc[:,10].name).agg({canceled.iloc[:,0].name: 'count'}).reset_index(0)
            canceled[canceled.iloc[:,0].name] = pd.to_datetime(canceled[canceled.iloc[:,0].name])
            canceled = canceled.rename(columns={canceled.iloc[:,0].name: "ds", canceled.iloc[:,1].name: "y"})
            canceled = filter_data_df(df, )
            canceled = canceled[(canceled['ds'] > '01/01/2024') & (canceled['ds'] < '12/10/2024')]
            canceled = prepare_data_prophet(canceled)
            steps = 98
            data_train = prepare_data_train(canceled, steps)
            data_test = prepare_data_test(canceled, steps)
            model = train_model(data_train)
            forecast = predict(model, predict_days, 'D') 
            return forecast
        case 'all':
            active = df[df[df.iloc[:,5].name] == 'active']
            active = prepare_df(active)
            finished = df[df[df.iloc[:,5].name] == 'finished']
            finished = prepare_df(finished)
            canceled = df[(df[df.iloc[:,10].name].notna()) & (df['state'] == 'canceled')]
            canceled = canceled[(canceled[canceled.iloc[:,10].name].notna()) & (canceled['state'] == 'canceled')]
            canceled[canceled.iloc[:,10].name] = canceled[canceled.iloc[:,10].name].str.slice(0,10)
            canceled = canceled.groupby(canceled.iloc[:,10].name).agg({canceled.iloc[:,0].name: 'count'}).reset_index(0)
            canceled[canceled.iloc[:,0].name] = pd.to_datetime(canceled[canceled.iloc[:,0].name])
            canceled = canceled.rename(columns={canceled.iloc[:,0].name: "ds", canceled.iloc[:,1].name: "y"})
            
            active = prepare_df(active,'01/01/2024','30/03/2025')
            active = prepare_data_prophet(active)
            finished = filter_data_df(finished,'01/01/2024','11/11/2024')
            finished = prepare_data_prophet(finished)
            canceled = filter_data_df(canceled,'01/01/2024','12/10/2024')
            canceled = prepare_data_prophet(canceled)

            steps = 50
            data_train = prepare_data_train(active, steps)
            data_test = prepare_data_test(active, steps)
            model = train_model(data_train)
            forecast_active = predict(model, predict_days, 'D') 

            steps = 89
            data_train = prepare_data_train(finished, steps)
            data_test = prepare_data_test(finished, steps)
            model = train_model(data_train)
            forecast_finished = predict(model, predict_days, 'D') 
            

            steps = 98
            data_train = prepare_data_train(canceled, steps)
            data_test = prepare_data_test(canceled, steps)
            model = train_model(data_train)
            forecast_canceled = predict(model, predict_days, 'D') 
            return [forecast_active,forecast_finished,forecast_canceled]

def prepare_df(df):
    df = df[[df.iloc[:,0].name,df.iloc[:,8].name]]
    df = df.groupby(df.iloc[:,1].name).agg({df.iloc[:,0].name: 'count'}).reset_index(0)
    df[df.iloc[:,0].name] = pd.to_datetime(df[df.iloc[:,0].name])
    df = df.rename(columns={df.iloc[:,0].name: "ds", df.iloc[:,1].name: "y"})
    return df

def filter_data_df(df, firstDate: str, limitDate:str):
    df = df[(df['ds'] > firstDate) & (df['ds'] < limitDate)]
    return df

def prepare_data_prophet(df):
    df = df.set_index('ds')
    df = df.asfreq('D', fill_value=0.0)
    df = df.sort_index()
    df = df.reset_index(0)
    return df

def prepare_data_train(df, steps: int):
    data_train = df[:-steps]
    return data_train

def prepare_data_test(df, steps:int):
    data_test  = df[-steps:]
    return data_test

def train_model(train_data):
    model = Prophet(weekly_seasonality=True, daily_seasonality=False, yearly_seasonality=True)
    model.fit(train_data)
    return(model)

def predict(model, period:int,freq: str):
    next_m = model.make_future_dataframe(periods=period, freq=freq)
    forecast = model.predict(next_m)
    return forecast