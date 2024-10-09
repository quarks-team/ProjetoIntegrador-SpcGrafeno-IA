import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")  # URL do banco de dados
    secret_key: str = os.getenv("SECRET_KEY", "mysecret")  # Chave secreta para autenticação
    api_v1_prefix: str = "/api/v1"  # Prefixo da API

    class Config:
        env_file = ".env"  # Arquivo de variáveis de ambiente

settings = Settings()
