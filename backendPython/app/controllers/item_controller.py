from fastapi import APIRouter
from app.schemas.item import ItemCreate, ItemResponse
from app.services.item_service import ItemService

router = APIRouter()
item_service = ItemService()

@router.post("/items/", response_model=ItemResponse)
def create_item(item: ItemCreate):
    return item_service.create_item(item)