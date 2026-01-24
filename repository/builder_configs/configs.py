from dataclasses import dataclass, field
from typing import Any

from .types import FilterType, OrderByType, LazyLoadType, FilterLogicType, UNSET



@dataclass
class Filter:
	column: str
	value: Any
	filter_type: FilterType = FilterType.EQ
 

@dataclass
class FilterConfig:
     filters: list[Filter]
     mode: FilterLogicType = FilterLogicType.NULL

@dataclass
class OrderByConfig:
	column: str
	mode: OrderByType = OrderByType.ASC
     
     
@dataclass
class ColumnConfig:
     column: str
     label: str | None = None
     value: Any = UNSET
     filter_type: FilterType = FilterType.EQ
     value_is_column: bool = False
     

@dataclass
class JoinConfig:
	table_name: str
	columns: list[ColumnConfig] = field(default_factory=list)
	filters: list[FilterConfig] = field(default_factory=list)
	order_by: list[OrderByConfig] = field(default_factory=list)


@dataclass
class LazyLoadConfig:
     relationship_strategy: str
     load_type: LazyLoadType = LazyLoadType.JOINEDLOAD