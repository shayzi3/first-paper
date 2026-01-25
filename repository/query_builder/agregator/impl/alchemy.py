from typing import Any
from sqlalchemy import func
from sqlalchemy.orm.properties import MappedColumn
from repository.builder_configs.types import FilterType


class SQLAlchemyAgregateFilterType:
     
     def filter_agregate(
          self, 
          value: Any, 
          filter_type: FilterType, 
          mapped_column: MappedColumn[Any],
          *args,
          **kwargs
     ) -> Any:
          operator_with_lambda = {
               "=": lambda column, value: column == value,
               ">": lambda column, value: column > value,
               ">=": lambda column, value: column >= value,
               "<": lambda column, value: column < value,
               "<=": lambda column, value: column <= value,
               "in": lambda column, value: column.in_(value),
               "vector_sort": lambda column, value: column.op("@@")(func.websearch_to_tsquery(str(value)))
          }
          if filter_type.value not in operator_with_lambda:
               raise ValueError(f"Not found operator {filter_type.value}")
          return operator_with_lambda[filter_type.value](mapped_column, value)