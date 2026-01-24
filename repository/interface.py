from typing import Any, Protocol, TypeVar, Generic

from .query_builder.interface import QueryBuilderProtocol
from .query_builder.agregator.interface import AgregateFilterTypeProtocol
from .builder_configs.configs import (
     FilterConfig,
     ColumnConfig,
     JoinConfig,
     OrderByConfig,
     LazyLoadConfig
)
from .impl.mixins.interfaces import UserRepositoryMixinProtocol


DTO = TypeVar("DTO")



class RepositoryProtocol(
     Generic[DTO],
     UserRepositoryMixinProtocol,
     Protocol,
):
     
     def __init__(self, session: Any, *args, **kwargs) -> None:
          self.session = session
          self._query_builder = QueryBuilderProtocol
          self._agregate = AgregateFilterTypeProtocol
     
     
     async def read(
          self,
          filters: list[FilterConfig] = [],
          columns: list[ColumnConfig] = [],
          joins: list[JoinConfig] = [],
          order_by: list[OrderByConfig] = [],
          loads: list[LazyLoadConfig] = [],
          offset: int | None = None,
          limit: int | None = None,
          count: bool = False,
          is_many: bool = False
     ) -> DTO | list[DTO] | dict[str, Any] | list[dict[str, Any]] | None:
          raise NotImplementedError
     
     