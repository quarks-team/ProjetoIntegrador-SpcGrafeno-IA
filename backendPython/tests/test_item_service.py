import pytest
from app.services.item_service import ItemService
from app.schemas.item import ItemCreate

class MockItemRepository:
    def create_item(self, item: ItemCreate):
        return {"id": 1, **item.dict()}  # Simulação de retorno do repositório

def test_create_item():
    item_service = ItemService()
    item_service.repository = MockItemRepository()  # Substituir pelo mock
    item_data = ItemCreate(name="Test Item", description="Test Description")
    
    result = item_service.create_item(item_data)

    assert result["id"] == 1
    assert result["name"] == "Test Item"
    assert result["description"] == "Test Description"
