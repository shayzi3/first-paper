from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..query_builder.impl.alchemy import SQLAlchemyQueryBuilder
from ..query_builder.agregator.impl.alchemy import SQLAlchemyAgregateFilterType
from ..builder_configs.configs import (
     FilterConfig,
     ColumnConfig,
     JoinConfig,
     OrderByConfig,
     LazyLoadConfig
)




class SQLAlchemyRepository:
     model = None
     
     def __init__(self) -> None:
          self._query_builder = SQLAlchemyQueryBuilder
          self._agregator = SQLAlchemyAgregateFilterType()
     
     async def read(
          self,
          session: AsyncSession,
          filter: list[FilterConfig] = [],
          columns: list[ColumnConfig] = [],
          join: list[JoinConfig] = [],
          order_by: list[OrderByConfig] = [],
          load: list[LazyLoadConfig] = [],
          limit: int | None = None,
          offset: int | None = None,
          count: bool = False,
          many: bool = False
     ) -> None | list[dict[str, Any]] | dict[str, Any]:
          query = (
               self._query_builder(
                    query_type=select,
                    model=self.model,
                    filter_agregate=self._agregator
               ).
               filter(filters=filter).
               columns(columns=columns).
               join(joins=join).
               order_by(order_by=order_by).
               load(loads=load).
               limit(limit).
               offset(offset)
          )
          if count is True:
               query = query.count()
               
          result = await session.execute(query.build())
          if many is True:
               result = (
                    result.scalars().all() 
                    if not columns else result.mappings().all()
               )
          else:
               result = (
                    result.scalar()
                    if not columns else result.mappings().first()
               )
          if not result:
               return None
          return result
               
          
               
          
          
     