# app/controllers/data_controller.py

from fastapi import HTTPException
from ..services.data_service import DataService

class DataController:
    def __init__(self, db_params):
        self.data_service = DataService(db_params)

    def handle_data_processing(self, file_path):
        """Processa o arquivo de dados e insere no banco de dados."""
        try:
            self.data_service.process_data(file_path)
            return {"message": "Dados processados e inseridos com sucesso."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
