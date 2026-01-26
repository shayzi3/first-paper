> [!NOTE]
> Repository - паттерн, позволяющий инкапсулировать логику работы с базой данных.

Созданием статьи и этого github репозитория послужило моё негодование по поводу 
полной бесполезности тех принципов, которые можно найти в видео на Youtube.
В статье представлена гибкая реализация построения сложных запросов при помощи конфигов,
обрабатывающихся дополнительным слоем - ORM QueryBuilder. Подробнее об этом вы можете
прочитать здесь.

Также в этом репозитории представлен новый способ работы с паттерном Repository. Про
это я бы и хотел здесь рассказать.

> [!TIP]
> Смысл моего способа заключается в том, что вместо создания кучи дополнительных классов, в которых постоянно
> перезаписывается атрибут `model`, можно создавать миксины и наследовать их в интерфейс/реализацию.
> Самое главное это то, что миксины создаются `только при необходимости`, а именно если не хватает
> логики методов представленных в имплементации интерфейса Repository.

Теперь, думаю, стоит показать примеры коды для большей ясности.

#### `Устаревший` Repository
```python
class RepositoryProtocol(Generic[DTO], Protocol):

     def __init__(self, session: Any, *args, **kwargs) -> None:
          self._session = session

     async def read(self, *args, **kwargs) -> DTO:
          raise NotImplementedError


class SQLAlchemyRepository(Generic[DTO]):
     model = None

     def __init__(self, session: AsyncSession) -> None:
          self._session = session

     async def read(self, *args, **kwargs) -> DTO:
          """Некоторый блок кода"""

# После чего для каждой модели
# создаётся отдельный класс, в котором перезаписывается атрибут `model`

# Предположим, есть две SQLAlchemy модели User и Post, также пусть будут UserDTO и PostDTO
# Для классов ниже должен быть создан интерфейс.

class UserRepositoryProtocol(RepositoryProtocol[UserDTO]):
     ...

class PostRepositoryProtocol(RepositoryProtocol[PostDTO]):
     ...


class SQLAlchemyUserRepository(SQLAlchemyRepository[UserDTO]):
     model = User

class SQLAlchemyPostRepository(SQLAlchemyRepository[PostDTO]):
     model = Post
```

#### Теперь посмотрим на реализацию паттерна Unit Of Work с `Устаревшим` Repository.
```python
class UnitOfWorkProtocol(Protocol):

     def __init__(self, *args, **kwargs) -> None:
          self._session_factory = None
          self._session = None

     async def __aenter__(self, *args, **kwargs) -> Self:
          raise NotImplementedError

     async def __aexit__(self) -> None:
          raise NotImplementedError

     def commit(self, *args, **kwargs) -> None:
          raise NotImplementedError

     def close(self, *args, **kwargs) -> None:
          raise NotImplementedError

     def rollback(self, *args, **kwargs) -> None:
          raise NotImplementedError

     @property
     def user(self) -> UserRepositoryProtocol:
          raise NotImplementedError

     @property
     def post(self) -> PostRepositoryProtocol:
          raise NotImplementedError


class SQLAlchemyUnitOfWork:
     def __init__(self, *args, **kwargs) -> None:
          self._session_factory = async_sessionmaker(async_engine)
          self._session = None

     async def __aenter__(self, *args, **kwargs) -> Self:
          """некоторый блок кода""""

     async def __aexit__(self) -> None:
          """некоторый блок кода""""

     def commit(self, *args, **kwargs) -> None:
          """некоторый блок кода""""

     def close(self, *args, **kwargs) -> None:
          """некоторый блок кода""""

     def rollback(self, *args, **kwargs) -> None:
          """некоторый блок кода""""

     @property
     def user(self) -> SQLAlchemyUserRepository:
          return SQLAlchemyUserRepository(session=self._session)

     @property
     def post(self) -> SQLAlchemyPostRepository:
          return SQLAlchemyPostRepository(session=self._session)
```
Основная проблема здесь заключается в том, что у нас добавляются лишние классы и 
соответственно появляется всё больше и больше интерфейсов. Эти классы это
`SQLAlchemyUserRepository` и `SQLAlchemyPostRepository`. UnitOfWork я привёл
в пример, потому что эти самые классы используются в качестве
аннотаций в интерфейсе и реализации, это не особо удобно когда таких классов
становится больше. Новый подход направлен на избаление от лишней абстракции.


#### `Новый` Repository
```python
class RepositoryProtocol(Generic[DTO], Protocol):

     def __init__(self, session: Any, *args, **kwargs) -> None:
          self._session = session

     async def read(self, *args, **kwargs) -> DTO:
          raise NotImplementedError

# Всё остаётся тоже самое, но model из атрибута класса перекочевал в атрибут экземпляра класса.

class SQLAlchemyRepository(Generic[DTO]):

     def __init__(self, session: AsyncSession, model: Any) -> None:
          self._model = model
          self._session = session

     async def read(self, *args, **kwargs) -> DTO:
          """Некоторый блок кода"""
```

#### Теперь Unit Of Work с `Новым` Repository.
```python
class UnitOfWorkProtocol(Protocol):

     def __init__(self, *args, **kwargs) -> None:
          self._session_factory = None
          self._session = None

     async def __aenter__(self, *args, **kwargs) -> Self:
          raise NotImplementedError

     async def __aexit__(self) -> None:
          raise NotImplementedError

     def commit(self, *args, **kwargs) -> None:
          raise NotImplementedError

     def close(self, *args, **kwargs) -> None:
          raise NotImplementedError

     def rollback(self, *args, **kwargs) -> None:
          raise NotImplementedError

     @property
     def user(self) -> RepositoryProtocol[UserDTO]:
          raise NotImplementedError

     @property
     def post(self) -> RepositoryProtocol[PostDTO]:
          raise NotImplementedError


class SQLAlchemyUnitOfWork:
     def __init__(self, *args, **kwargs) -> None:
          self._session_factory = async_sessionmaker(async_engine)
          self._session = None

     async def __aenter__(self, *args, **kwargs) -> Self:
          """некоторый блок кода""""

     async def __aexit__(self) -> None:
          """некоторый блок кода""""

     def commit(self, *args, **kwargs) -> None:
          """некоторый блок кода""""

     def close(self, *args, **kwargs) -> None:
          """некоторый блок кода""""

     def rollback(self, *args, **kwargs) -> None:
          """некоторый блок кода""""

     @property
     def user(self) -> SQLAlchemyRepository[UserDTO]:
          return SQLAlchemyUserRepository(session=self._session, model=User)

     @property
     def post(self) -> SQLAlchemyRepository[PostDTO]:
          return SQLAlchemyPostRepository(session=self._session, model=Post)
```
В данной реализации получилось избавиться от лишних классов и интерфейсов, остались только
`SQLAlchemyRepository` и `RepositoryProtocol`.

Ну где же тут миксины?

В этом и суть, что их нужно делать только тогда, когда нам нужна логика, которую
не может предоставить имплентация интрефейса, в данном случае `SQLAlchemyRepository`.

Допустим, нам понадобился метод, для User.
```python
class UserMixinProtocol(Protocol):

     async def method_only_for_user(self, *args, **kwargs) -> list[UserDTO]:
          raise NotImplentedError

class SQLAlchemyUserMixin:
     mixin_model = User

     async def method_only_for_user(self, *args, **kwargs) -> list[UserDTO]:
          """некоторый блок кода"""

# Что же дальше?
# Дальше - наследование этих классов в RepositoryProtocol и SQLAlchemyRepository

class RepositoryProtocol(
     Generic[DTO], 
     UserMixinProtocol,
     Protocol
):
     """некоторый блок кода"""


class SQLAlchemyRepository(
     Generic[DTO],
     SQLAlchemyUserMixin
):
     """некоторый блок кода"""
```

После создания миксина всё же появляется дополнительная абстракция, но если
в `Устаревшем` варианте Repository создавать эту абстракцию необходимость, то в `Новом`
это нужно делать лишь тогда, когда не хватает логики методов имплементации интерфейса. При этом
миксины не выходят за рамки Repository, тоесть не появляются, например, в Unit of Work. Это значительно
упрощает разработку.