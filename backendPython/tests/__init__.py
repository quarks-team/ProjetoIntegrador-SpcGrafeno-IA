# tests/__init__.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def test_client():
    """
    Fixture to provide a test client for FastAPI routes.
    This client is used to test the API endpoints.
    """
    client = TestClient(app)
    yield client  # Provides the fixture value and later performs cleanup
