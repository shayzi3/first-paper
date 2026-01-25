from typing import Protocol

from schema.dto import MarketItemDTO
from repository.builder_configs.types import OrderByType, FilterType


class MarketItemServiceProtocol(Protocol):
     
     async def paginate_market_items(
          self,
          categories: list[str] = [],
          full_name: str | None = None,
          wear: list[str] = [],
          price: float | None = None,
          price_order_by: OrderByType | None = None,
          price_filter_type: FilterType | None = None,
          *args,
          **kwargs
     ) -> list[MarketItemDTO]:
          """Метод возвращает все продаваемые предметы по определённым фильтрам вместе с продавцами"""
          raise NotImplementedError