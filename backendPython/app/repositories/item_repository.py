from app.entities.item import Item
from app.schemas.item import ItemCreate

class ItemRepository:
    def create_item(self, item: ItemCreate) -> Item:
        # Implementar a lógica de inserção no banco de dados aqui
        new_item = Item(**item.dict())
        # Salvar new_item no banco de dados
        return new_item
