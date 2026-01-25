from typing import Callable, Any, TypeVar
from typing_extensions import Self

from sqlalchemy.orm.relationships import _RelationshipDeclared
from sqlalchemy.orm.properties import MappedColumn
from sqlalchemy.sql.elements import ColumnElement, Label, UnaryExpression
from sqlalchemy.orm.strategy_options import _AbstractLoad
from sqlalchemy import or_, and_, func, asc, desc
from sqlalchemy.orm import MappedColumn, joinedload, selectinload

from db.models import Base
from repository.builder_configs.configs import (
     FilterConfig,
     ColumnConfig,
     JoinConfig,
     OrderByConfig,
     LazyLoadConfig
)
from repository.builder_configs.types import LazyLoadType, OrderByType, FilterLogicType, UNSET
from ..agregator.interface import AgregateFilterTypeProtocol


ALCHEMYMODEL = TypeVar("ALCHEMYMODEL", bound=Base)


class SQLAlchemyQueryBuilder:

     
     def __init__(
          self,
          query_type: Callable,
          model: type[ALCHEMYMODEL],
          filter_agregate: AgregateFilterTypeProtocol,
          *args,
          **kwargs
     ) -> None:
          self._query_type: Callable = query_type # select, insert, update, delete
          self._filter_agregate: AgregateFilterTypeProtocol = filter_agregate
          self._model: type[ALCHEMYMODEL] = model
          
          self._columns: list[MappedColumn[Any] | ColumnElement[bool] | Label[Any]] = []
          self._limit: int | None = None
          self._offset: int | None = None
          self._joins: list[type[ALCHEMYMODEL]] = []
          self._filter: list[ColumnElement[bool]] = []
          self._order_by: list[UnaryExpression] = []
          self._values: list[dict[str, Any]] = []
          self._loads: list[_AbstractLoad] = []
          self._count: bool = False
          self._orm_models: dict[str, type["Base"]] = model.orm_models()
          
     def count(self) -> Self:
          self._count = True
          return self
          
          
     def columns(
          self, 
          columns: list[ColumnConfig] = [], 
          model: type[ALCHEMYMODEL] | None = None,
          *args,
          **kwargs
     ) -> Self:
          if columns:
               if model is None:
                    model = self._model
                    
               for config in columns:
                    obj = getattr(model, config.column, None)
                    if (obj is None):
                         raise ValueError(f"model {model.__name__} has not column {config.column}")
                    
                    if config.value is not UNSET:
                         if config.value_is_column is True:
                              table_name, column_name = config.value.split(".")
                              orm_object = self._orm_models.get(table_name)

                              if (hasattr(orm_object, column_name) is False):
                                   raise ValueError(f"model {orm_object} has not column {column_name}")

                              config.value = getattr(orm_object, column_name)
                              
                         obj = self._filter_agregate.filter_agregate(
                              mapped_column=obj,
                              value=config.value,
                              filter_type=config.filter_type
                         )
                         
                    if config.label is not None:
                         obj = obj.label(config.label)
                    self._columns.append(obj)
          return self
          
          
     def filter(
          self, 
          filters: list[FilterConfig] = [],
          model: type[ALCHEMYMODEL] | None = None,
          *args,
          **kwargs
     ) -> Self:
          if filters:
               if model is None:
                    model = self._model
                    
               configs = []
               for filter in filters:
                    mode = None
                    if filter.mode == FilterLogicType.OR:
                         mode = or_
                    elif filter.mode == FilterLogicType.AND:
                         mode = and_
                    
                    elements_objects = []
                    for filter_ in filter.filters:
                         obj = getattr(model, filter_.column, None)
                         if (obj is None):
                              raise ValueError(f"model {model.__name__} has not column {filter_.column}")
                         
                         column_element = self._filter_agregate.filter_agregate(
                              mapped_column=obj,
                              filter_type=filter_.filter_type,
                              value=filter_.value
                         )
                         elements_objects.append(column_element)
                         
                    if mode is None:
                         configs.extend(elements_objects)
                    else:
                         configs.append(mode(*elements_objects))
                         
               if configs:
                    self._filter.extend(configs)
          return self
     
     def order_by(
          self, 
          order_by: list[OrderByConfig] = [], 
          model: type[ALCHEMYMODEL] | None = None,
          *args,
          **kwargs
     ) -> Self:
          if order_by:
               if model is None:
                    model = self._model
                    
               for oby in order_by:
                    oby_mode = asc
                    if oby.mode == OrderByType.DESC:
                         oby_mode = desc
                    
                    obj = getattr(model, oby.column, None)
                    if (obj is None):
                         raise ValueError(f"model {model.__name__} has not column {oby.column}")
                    
                    self._order_by.append(oby_mode(obj))
          return self
     
     def join(self, joins: list[JoinConfig]) -> Self:
          if joins:
               for join in joins:
                    orm_object = self._orm_models.get(join.table_name)
                    if join.columns:
                         self.columns(
                              columns=join.columns,
                              model=orm_object
                         )
                    if join.filters:
                         self.filter(
                              filters=join.filters,
                              model=orm_object
                         )
                    if join.order_by:
                         self.order_by(
                              order_by=join.order_by,
                              model=orm_object
                         )
                    self._joins.append(orm_object)
          return self
          
          
     def load(
          self, 
          loads: list[LazyLoadConfig], 
          model: type[Base] | None = None,
          *args,
          **kwargs
     ) -> Self:
          if loads:
               for load in loads:
                    load_mode = joinedload
                    if load.load_type == LazyLoadType.SELECTINLOAD:
                         load_mode = selectinload
                     
                    current_model = model  
                    if model is None:
                         current_model = self._model
                    
                    current_load = None
                    relationship_path = load.relationship_strategy.split(".")
                    
                    for part in relationship_path:
                         relationship_declared = getattr(current_model, part, None)
                         if (relationship_declared is None):
                              raise ValueError(f"Error in relationship path: model {current_model.__name__} has no relationship {part}")
                         
                         current_model = relationship_declared.mapper.class_
                         if current_load is None:
                              current_load = load_mode(relationship_declared)
                         else:
                              current_load = getattr(current_load, load_mode.__name__)(relationship_declared)
                              
                    if current_load:
                         self._loads.append(current_load)
          return self
     
     
     def values(
          self,
          data: dict[str, Any] | list[dict[str, Any]]
     ) -> Self:
          if isinstance(data, dict):
               self._values.append(data)
          elif isinstance(data, list):
               self._values.extend(data)
          return self
     
          
     def limit(
          self,
          value: int | None = None
     ) -> Self:
          if value:
               self._limit = value
          return self
     
     
     def offset(
          self,
          value: int | None = None
     ) -> Self:
          if value:
               self._offset = value
          return self
     
          
     def build(
          self
     ) -> Any:
          query = self._query_type(self._model)

          if self._columns:
               query = self._query_type(*self._columns).select_from(self._model)
               
          if self._count:
               count = func.count()
               if self._columns:
                    count = func.count(*self._columns)
                    
               query = self._query_type(count).select_from(self._model)
               
          if self._values:
               query = query.values(self._values)
               
          if self._filter:
               query = query.filter(*self._filter)
               
          if self._joins:
               for join in self._joins:
                    query = query.join(join)
                    
          if self._order_by:
               query = query.order_by(*self._order_by)
               
          if self._loads:
               query = query.options(*self._loads)
               
          if self._limit:
               query = query.limit(self._limit)
          
          if self._offset:
               query = query.offset(self._offset)
          return query