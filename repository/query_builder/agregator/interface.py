from typing import Protocol, Any

from sqlalchemy.orm.properties import MappedColumn

from repository.builder_configs.types import FilterType


class AgregateFilterTypeProtocol(Protocol):
     
     def filter_agregate(
          self, 
          value: Any, 
          filter_type: FilterType, 
          mapped_column: MappedColumn,
          *args,
          **kwargs
     ) -> Any:
          raise NotImplementedError