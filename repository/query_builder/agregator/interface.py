from typing import Protocol, Any

from repository.builder_configs.types import FilterType


class AgregateFilterTypeProtocol(Protocol):
     
     def filter_agregate(
          self, 
          value: Any, 
          filter_type: FilterType, 
          *args,
          **kwargs
     ) -> Any:
          raise NotImplementedError