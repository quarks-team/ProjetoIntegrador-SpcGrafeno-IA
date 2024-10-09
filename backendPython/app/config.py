# app/config.py

import os
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis do .env

class DatabaseConfig:
    @staticmethod
    def get_params():
        return {
            "host": os.getenv("DATABASE_HOST"),
            "port": os.getenv("DATABASE_PORT"),
            "user": os.getenv("DATABASE_USER"),
            "password": os.getenv("DATABASE_PASSWORD"),
            "dbname": os.getenv("DATABASE_NAME"),
        }
