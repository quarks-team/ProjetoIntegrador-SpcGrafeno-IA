# app/main.py

from fastapi import FastAPI
from app.controllers.data_controller import DataController
from app.config import DatabaseConfig

app = FastAPI()

db_params = DatabaseConfig.get_params()
data_controller = DataController(db_params)

@app.on_event("startup")
async def startup_event():
    # Aqui você pode fazer inicializações se necessário
    print("FastAPI is starting up...")

@app.post("/process-data/")
async def process_data(file_path: str):
    """Processa os dados do arquivo Excel e insere no banco de dados."""
    return data_controller.handle_data_processing(file_path)

@app.get("/")
async def root():
    """Endpoint raiz."""
    return {"message": "API está funcionando. Acesse /docs para ver a documentação."}

