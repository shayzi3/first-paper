from typing import Protocol

from schema.dto import ItemDTO


class ItemServiceProtocol(Protocol):
     
     async def get_item_with_market_items(self, id: int, *args, **kwargs) -> ItemDTO | None:
          """Метод возвращает предмет, который имеет список продаваемых предметов соответственно."""
          raise NotImplementedError
     
     async def get_items_of_categories(self, categories: list[str], *args, **kwargs) -> list[ItemDTO]:
          """Метод возвращает предметы определённых категорий"""
          raise NotImplementedError