from typing import Any
from repository.builder_configs.types import FilterType


class SQLAlchemyAgregateFilterType:
     
     def filter_agregate(
          self, 
          value: Any, 
          filter_type: FilterType, 
          mapped_column: Any,
          *args,
          **kwargs
     ) -> Any:
          operator_with_lambda = {
               "=": lambda column, value: column == value,
               ">": lambda column, value: column > value,
               ">=": lambda column, value: column >= value,
               "<": lambda column, value: column < value,
               "<=": lambda column, value: column <= value,
          }
          if filter_type.value not in operator_with_lambda:
               raise ValueError(f"Not found operator {filter_type.value}")
          return operator_with_lambda[filter_type.value](mapped_column, value)