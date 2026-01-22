Cложные запросы через паттерн Repository. Large Repository

Салют Хабр! Меня зовут Влад и я хотел бы осветить довольно важную тему, которую я не видел в обучающих материалах, а именно сложные запросы через паттерн Repository.

Проблема: построение гибких SQLAlchemy запросов на основе данных, переданных
из бизнес логики. Поддержка различных форматов в запросах. Более масштабное использование
паттерна Repository.

Решение(то, о чём говорится в этой статье): все запросы формируются посредством конфигов,
переданных из бизнес логики, далее конфиги парсятся и из них составляется ORM запрос.

Схема работы реализации:

![](https://github.com/shayzi3/first-paper/blob/images/scheme.png)

Добавляются 3 новых слоя: `Configs`, `ORM Query Builder`, `Operator Agregate`

Актуальность для читателя: я думаю, что моё решение этой проблемы может
показать работу с паттерном Repository под другим углом, показать как можно
строить гибкие запросы без создания кучи методов в имплементациях и потом описывания
этих же методов в интерфейсах.

Пожалуй, можно начинать.

Все вы видели те самые классы, которые мелькают в видосах на Youtube.
```python
from typing import Generic, TypeVar, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

DTO = TypeVar("DTO")

class SQLAlchemyRepository(Generic[DTO]):
	model = None

	def __init__(self, session: AsyncSession) -> None:
		self._session = session

	async def get_by_filter(self, filters: dict[str, Any]) -> DTO | None:
		query = select(self.model).filter_by(**filters)
		data = await self._session.execute(query)

		data_scalar = data.scalar()
		if data_scalar is None:
			return None
		
		return data_scalar.to_dto()


	async def get_many_by_filter(self, filters: dict[str, Any]) -> list[DTO]:
		query = select(self.model).filter_by(**filters)
		data = await self._session.execute(query)
		
		data_all = data.scalars().all()
		if not data_all:
			return []
		
		return [sqal_model.to_dto() for sqal_model in data_all]
```
При росте вашего проекта вам понадобятся более кастомизированные запросы и логики этих методов хватать не будет, соответственно вам придётся расширяться.

Как уже упоминалось в `Решение` используются конфиги, думаю, сейчас лучший момент, чтобы
их продемонстировать, но для начала нужно объявить структуру проекта.

* repository
    * builder_configs
        * \_\_init__.py
        * configs.py
        * types.py

#### repository/builder_configs/configs.py
```python
from dataclasses import dataclass, field
from typing import Any

from .types import FilterType, OrderByType, LazyLoadType, FilterLogicType

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
    label: str | UNSET = UNSET
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
```
Хочу поподробней остановиться на фильрах.
- Filter - простой в реализации датакласс, который принимает на вход поле, значение и
необходимый оператор сравнения.
- FilterConfig - в него можно передавать несколько фильтров и применять к ним логическое условие OR, AND. В случае если условие передано не будет(NULL), то все агрегированные объекты будут присутствовать в SQL запросе через запятую.
- OrderByConfig - сортировка поля по заданному режиму(ASC, DESC)
- ColumnConfig - этот датакласс позволяет включать в SQL запрос выборку отдельных колонок, задавать им label, также он позволяет делать булевые выборки с указанным значением, также есть поддержка не только значений, но и отдельных колонок из других таблиц. Для этого нужно: `value=table_name.column`, `value_is_column=True`. Важно, чтобы таблица table 
- JoinConfig - позволяет присоединять другие таблицы. Переданные атрибуты `columns`, `filters`, `order_by` будут использованны для конкретной таблицы `table_name`.
- LazyLoadConfig - поддержка подгрузки relationship. Чтобы подгрузить нужно указать название relationhip атрибута. Если же вы хотите получить вложенное отношение, то нужно указывать relationship по цепочке через `.`

    - Пример подгрузки вложенных отношений: 
        Допустим, есть модель User и она имеет отношение с таблицей Item через атрибут `item`, также Item связана с другой таблицей Collections посредством отношения `collections` и вот здесь и появляются вложенные отношения. Представим, что выполняется запрос в таблицу User и понадобилось подтянуть отношение item и к нему collections. В таком случае `relationship_strategy=item.collections`. Более подробно это будет рассмотрено при разборе реализации метода `load` класса SQLAlchemyQueryBuilder.


####  repository/builder_configs/types.py
```python
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
 
class LoadType(Enum):
    JOINEDLOAD = "joinedload"
    SELECTINLOAD = "selectinload"
```
Всё, что находится в `FilterType` должен содержать `Operator Agregate`.

На блок схеме вы могли заметить, что от `Configs` идут стрелки на 3 других блока,
возможно, вы уже догадались в чём дело, но если нет вот объяснение: конфиги являются
независимой не от чего частью, и их применение можно найти в 3-ёх слоях `Бизнес логика`, `Repository`, `ORM Query Builder`.

Теперь я хотел бы затронуть сам `ORM Query Builder`. Структура папок в свою очередь принимает такой вид:
* repository
    * builder_configs
        * \_\_init__.py
        * configs.py
        * types.py
    * query_builder
        * \_\_init__.py
        * interface.py
        * impl
            * \_\_init__.py
            * alchemy.py


Интерфейс для Query Builder:
#### repository/query_builder/interface.py
```python
from typing import Protocol, Any
from typing_extensions import Self

from repository.builder_configs.configs import (
    FilterConfig,
    ColumnConfig,
    JoinConfig,
    LazyLoadConfig,
    OrderByConfig
)
from .agregator.interface import AgregateFilterTypeProtocol


class QueryBuilderProtocol(Protocol):
     
     def __init__(
        self, 
        filter_agregate: AgregateFilterTypeProtocol, 
        *args, 
        **kwargs
    ) -> None:
        self._filter_agregate = filter_agregate
          
    def count(self) -> Self:
        raise NotImplementedError
    
    def columns(self, columns: list[ColumnConfig], *args, **kwargs) -> Self:
        raise NotImplementedError
    
    def filter(self, filters: list[FilterConfig], *args, **kwargs) -> Self:
        raise NotImplementedError
    
    def join(self, joins: list[JoinConfig]) -> Self:
        raise NotImplementedError
    
    def load(self, loads: list[LazyLoadConfig], *args, **kwargs) -> Self:
        raise NotImplementedError
    
    def order_by(self, order_by: list[OrderByConfig], *args, **kwargs) -> Self:
        raise NotImplementedError
    
    def values(self, data: dict[str, Any] | list[dict[str, Any]]) -> Self:
        raise NotImplementedError
    
    def limit(self, value: int | None) -> Self:
        raise NotImplementedError
    
    def offset(self, value: int | None) -> Self:
        raise NotImplementedError
    
    def build(self) -> Any:
        raise NotImplementedError
```

В магическом методе `__init__` вы можете заметить `AgregateFilterTypeProtocol` данный
протокол нужен для агрегации операторов сравнения таких как: >, =, >=, <, <= и тп.

С появлением агрегатора структура папок примет такой вид:
* repository
    * builder_configs
        * \_\_init__.py
        * configs.py
        * types.py
    * query_builder
        * \_\_init__.py
        * agregator
            * \_\_init__.py
            * interface.py
            * impl
                * \_\_init__.py
                * alchemy.py
        * interface.py
        * impl
            * \_\_init__.py
            * alchemy.py

Ниже вы можете увидеть интерфейс и реализацию агрегатора.
#### repository/query_builder/agregator/interface.py
```python
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
```

#### repository/query_builder/agregator/impl/alchemy.py
```python
from typing import Any
from sqlalchemy.orm.properties import MappedColumn
from repository.builder_configs.types import FilterType


class SQLAlchemyAgregateFilterType:
     
    def filter_agregate(
        self, 
        value: Any, 
        filter_type: FilterType, 
        mapped_column: MappedColumn,
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
```
В реализации вам может быть непонятен аргумент `mapped_column` - это экземпляр класса,
полученный из атрибута ORM модели. Этот атрибут обязательно должен быть полем в вашей
таблице.

Ну и теперь гвоздь программы `SQLAlchemyQueryBuilder`. Я буду объяснять каждый метод постепенно.

```python
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
        self._query_type: Callable = query_type
        self._filter_agregate: AgregateFilterTypeProtocol = filter_agregate
        self._model: type[ALCHEMYMODEL] = model
        
        self._columns: list[MappedColumn | ColumnElement[bool] | Label[Any]] = []
        self._limit: int | None = None
        self._offset: int | None = None
        self._joins: list[type[ALCHEMYMODEL]] = []
        self._filter: list[ColumnElement[bool]] = []
        self._order_by: list[UnaryExpression] = []
        self._values: list[dict[str, Any]] = []
        self._loads: list[_AbstractLoad] = []
        self._count: bool = False
        self._orm_models: dict[str, type["Base"]] = model.orm_models()
```
`query_type` - тип выполняемого запроса: `select`, `update` и тп.

`model` - orm модель

После создания экземпляра этого класса и при вызове методов данные накапливаются
в атрибутах и при вызове метода `build` строится ORM запрос.

Здесь можно обратить внимание на атрибут `_orm_models`, исходя из его аннотации
можно сказать, что он хранит все зарегестрированные sqlalchemy модели.

##### Реализация метода `orm_models`
```python
class Base(DeclarativeBase):
    _cached_orm_models: dict[str, type["Base"]] = {}

    @classmethod
    def orm_models(cls) -> dict[str, type["Base"]]:
        if not cls._cached_orm_models:
            models = {}
            for mapper in cls.registry.mappers:
                models[mapper.class_.__tablename__] = mapper.class_
            cls._cached_orm_models.update(models)
        return cls._cached_orm_models
```

### Теперь переходим к самим методам.

#### `count`
```python
    def count(self) -> Self:
        self._count = True
        return self
```
Позволяет получать количество нужных записей.

#### `columns`
```python
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
                if (obj is None) or (isinstance(obj, MappedColumn) is False):
                    raise ValueError(f"model {model.__name__} has not column {config.column}")
                
                if config.value is not UNSET:
                    if config.value_is_column is True:
                            table_name, column_name = config.value.split(".")
                            orm_object = self._orm_models.get(table_name)

                            if (hasattr(orm_object, column_name) is False) or (isinstance(obj, MappedColumn) is False):
                                raise ValueError(f"model {orm_object} has not column {column_name}")

                            config.value = getattr(orm_object, column_name)
                              
                        obj = self._filter_agregate.filter_agregate(
                            mapped_column=obj,
                            value=config.value,
                            filter_type=config.filter_type
                        )
                         
                if config.label not in (UNSET, None):
                    obj = obj.label(config.label)
                self._columns.append(obj)
          return self
```
В начале функции проверяется, была ли передана модель в функцию,
это нужно, чтобы переиспользовать метод для разных моделей(станет понятней после разбора метода `join`). Дальше - итерация, в которой я получаю у объекта `model` атрибут `config.column` и он всегда обязан быть `MappedColumn`. После идёт проверка на переданное значение
и если оно является полем в другой таблице, то я распиливаю строку по `.` и из `_orm_models` получаю нужную orm модель, после я записываю в `config.value` значение
атрибута `column_name`. Дальше работает агрегатор и как вы можете заметить в `config.value` может лежать как произвольное значение так и MappedColumn. Последнее это добавление label ну и окончательное действие это - запись получившегося объекта в список `_columns`.


#### `filter`
```python
    def filter(
            self, 
            filters: list[FilterConfig] = [],
            model: type[ALCHEMYMODEL] | None = None
        ) -> Self:
            if filters:
                if model is None:
                    model = self._model

                configs = []
                for filter in filters:
                    mode = lambda *any_: any_
                    if filter.mode == FilterLogicType.OR:
                        mode = or_
                    elif filter.mode == FilterLogicType.AND:
                        mode = and_

                    elements_objects = []
                    for filter_ in filter.filters:
                        obj = getattr(model, filter_.column, None)
                        if (obj is None) or (isinstance(obj, MappedColumn) is False):
                            raise ValueError(f"model {model.__name__} has not column {filter_.column}")

                            column_element = self._filter_agregate.filter_agregate(
                                mapped_column=obj,
                                filter_type=filter_.filter_type,
                                value=filter_.value
                            )
                            elements_objects.append(column_element)
                        if mode is None:
                            configs.append(mode(*elements_objects))
                        else:
                            elements_objects.extend(elements_objects)
                    if configs:
                        self._filter.extend(configs)
            return self
```
Итерация по `FilterConfig`, определение логического условия, после чего происходит итерация по `Filter`, в этом блоке кода также получаю MappedColumn и отправляю в агрегатор. В `element_objects` остаются все аргегированные `Filter`, в `elements` - `FilterConfig`. После завершения основного цикла изменения отправляются в атрибут `_filters`.   


#### `order_by`
```python
    def order_by(
            self, 
            order_by: list[OrderByConfig] = [], 
            model: type[ALCHEMYMODEL] | None = None,
            *args,
            **kwargs
        ) -> Self:
            if order_by:
                if model in None:
                    model = self._model

                for oby in order_by:
                    oby_mode = asc
                    if oby.order_by_type == OrderByType.DESC:
                        oby_mode = desc

                    obj = getattr(model, oby.column, None)
                    if (obj is None) or (isinstance(obj, MappedColumn) is False):
                        raise ValueError(f"model {model.__name__} has not column {oby.column}")
                    
                    self._order_by.append(oby_mode(obj))
            return self
```
Я думаю, что здесь объяснения излишни так как используются всё те же принципы, что и в предыдущих методах.

#### `join`
```python
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
```
Здесь можно заметить, что переиспользуются методы `filter`, `columns`, `order_by`, только
вместо изначально переданной в `__init__` orm модели, будет использована модель, название 
которой указано в конфиге, объект этой модели достаётся из `_orm_models`.

#### `load`
```python
    def load(self, loads: list[LazyLoadConfig]) -> Self:
        if loads:
            for load in loads:
                load_mode = joinedload
                if load.load_type == LazyLoadType.SELECTINLOAD:
                    load_mode = selectinload
                         
                current_model = self._model
                current_load = None
                relationship_path = load.relationship_strategy.split(".")
                    
                for part in relationship_path:
                    relationship_declared = getattr(current_model, part, None)
                    if (relationship_declared is None) or (isinstance(relationship_declared, _RelationshipDeclared) is False):
                        raise ValueError(f"Error in relationship path: model {current_model.__name__} has no relationship {part}")
                         
                    current_model = relationship_declared.mapper.class_
                    if current_load is None:
                        current_load = load_mode(relationship_declared)
                    else:
                        current_load = getattr(current_load, load_mode.__name__)(relationship_declared)
                              
                if current_load:
                    self._loads.append(current_load)
        return self
```
Здесь я бы хотел объяснить как именно обрабатывается relationship_strategy и как собираются вложенные relationship. Переменная `relationship_path` хранит все отношения, из которых составляется цепочка, итерируясь по ним `relationship_declared` получает экземпляр класса `_RelationshipDeclared` и после `current_model` перезаписывается на модель, с которой связано отношение. После чего формируется `current_load`, если оно не было до этого записано, то просто передаём отношение в функцию `load_mode`, иначе мы вызываем функцию `load_mode` у `current_load`. Пример: `joinedload(part1_relationship).joinedload(part2_relationship)`. Именно так и строятся вложенные relationship.

Теперь покажу несколько легковесных методов, в которых я думаю вы уже можете разобраться самостоятельно.

#### `values`, `limit`, `offset`
```python
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
```

#### `build`
```python
    def build(
        self
    ) -> Any:
        query = self._query_type(self._model)
          
        if self._columns:
            query = self._query_type(*self._columns)
               
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
```
Здесь, как мне кажется, комментарии тоже не нужны.


Больше сказать мне нечего, всё показал, всё рассказал. Надеюсь, что эта статья даст читающим новые мысли по поводу паттерна Repository и то как с ним можно работать. Очень надеюсь на конструктивную критику и буду рад, если вы предложите свои реализации решения данной проблемы.

В этом репозитории вы можете посмотреть примеры использования.

Спасибо тебе, дорогой читатьтель, за интерес к моей статье!