from typing import NewType
from enum import Enum


UNSET = NewType("UNSET", None)


class FilterLogicType(Enum):
     AND = "and"
     OR = "or"
     NULL = "null"

class FilterType(Enum):
	EQ = "="
	GT = ">"
	GE = ">="
	LT = "<"
	LE = "<="

class OrderByType(Enum):
	ASC = "asc"
	DESC = "desc"
 
class LazyLoadType(Enum):
     JOINEDLOAD = "joinedload"
     SELECTINLOAD = "selectinload"