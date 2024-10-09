from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemCreate, ItemResponse

class ItemService:
    def __init__(self):
        self.repository = ItemRepository()

    def create_item(self, item: ItemCreate) -> ItemResponse:
        return self.repository.create_item(item)