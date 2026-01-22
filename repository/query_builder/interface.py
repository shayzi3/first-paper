from typing import Protocol, Any
from typing_extensions import Self

from repository.builder_configs.configs import (
     FilterConfig,
     ColumnConfig,
     JoinConfig,
     LazyLoadConfig,
     OrderByConfig
)
from .agregator.interface import AgregateFilterTypeProtocol





class QueryBuilderProtocol(Protocol):
     
     def __init__(self, filter_agregate: AgregateFilterTypeProtocol, *args, **kwargs) -> None:
          self._filter_agregate = filter_agregate
          
     def count(self) -> Self:
          raise NotImplementedError
     
     def columns(self, columns: list[ColumnConfig], *args, **kwargs) -> Self:
          raise NotImplementedError
     
     def filter(self, filters: list[FilterConfig], *args, **kwargs) -> Self:
          raise NotImplementedError
     
     def join(self, joins: list[JoinConfig]) -> Self:
          raise NotImplementedError
     
     def load(self, loads: list[LazyLoadConfig], *args, **kwargs) -> Self:
          raise NotImplementedError
     
     def order_by(self, order_by: list[OrderByConfig], *args, **kwargs) -> Self:
          raise NotImplementedError
     
     def values(self, data: dict[str, Any] | list[dict[str, Any]]) -> Self:
          raise NotImplementedError
     
     def limit(self, value: int | None) -> Self:
          raise NotImplementedError
     
     def offset(self, value: int | None) -> Self:
          raise NotImplementedError
     
     def build(self) -> Any:
          raise NotImplementedError