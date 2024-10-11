# app/main.py

from fastapi import FastAPI
from app.config import DatabaseConfig

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

