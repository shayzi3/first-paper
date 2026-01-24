from typing import Any, TypeVar, Generic

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Base
from ..query_builder.impl.alchemy import SQLAlchemyQueryBuilder
from ..query_builder.agregator.impl.alchemy import SQLAlchemyAgregateFilterType
from ..builder_configs.configs import (
     FilterConfig,
     ColumnConfig,
     JoinConfig,
     OrderByConfig,
     LazyLoadConfig
)
from .mixins.alchemy import SQLAlchemyUserRepositoryMixin


DTO = TypeVar("DTO")


class SQLAlchemyRepository(
     Generic[DTO],
     SQLAlchemyUserRepositoryMixin
):
     
     def __init__(self, session: AsyncSession, model: type[Base], *args, **kwargs) -> None:
          self.model = model
          self._session = session
          self._query_builder = SQLAlchemyQueryBuilder
          self._agregator = SQLAlchemyAgregateFilterType()
     
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
          query = (
               self._query_builder(
                    query_type=select,
                    model=self.model,
                    filter_agregate=self._agregator
               ).
               filter(filters=filters).
               columns(columns=columns).
               join(joins=joins).
               order_by(order_by=order_by).
               load(loads=loads).
               limit(limit).
               offset(offset)
          )
          if count is True:
               query = query.count()
          
          result = await self._session.execute(query.build())
          if is_many:
               result = (
                    result.scalars().unique().all() 
                    if not columns else result.mappings().all()
               )
          else:
               result = (
                    result.scalar()
                    if not columns else result.mappings().first()
               )
          if not result:
               return None
          
          if columns:
               return result
          
          if is_many is True:
               return [model.dto() for model in result]
          else:
               return result.dto()
               
          
          
     
     
     
     