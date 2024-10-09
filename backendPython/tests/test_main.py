import pytest
from fastapi.testclient import TestClient
from app.main import app  # Altere o import conforme a estrutura do seu projeto

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is running!"}


def test_read_item():
    item_id = 42
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json() == {"item_id": item_id}
