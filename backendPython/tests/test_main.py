# test_main.py

import pytest
from fastapi.testclient import TestClient
from app.main import app  # Ajuste conforme a estrutura do seu projeto

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API está funcionando. Acesse /docs para ver a documentação."}
