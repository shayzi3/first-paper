from typing_extensions import Self, Protocol

from repository.interface import RepositoryProtocol
from schema.dto import UserDTO, ItemDTO, MarketItemDTO




class UnitOfWorkProtocol(Protocol):
     
     def __init__(self) -> None:
          self._sessionmaker = None
          self._session = None
          self._cached_repository = {}
     
     async def __aenter__(self) -> Self:
          raise NotImplementedError
     
     async def __aexit__(self) -> None:
          raise NotImplementedError
     
     async def commit(self) -> None:
          raise NotImplementedError
     
     async def rollback(self) -> None:
          raise NotImplementedError
     
     async def close(self) -> None:
          raise NotImplementedError
     
     @property
     def user(self) -> RepositoryProtocol[UserDTO]:
          raise NotImplementedError
     
     @property
     def item(self) -> RepositoryProtocol[ItemDTO]:
          raise NotImplementedError
     
     @property
     def market_item(self) -> RepositoryProtocol[MarketItemDTO]:
          raise NotImplementedError
     
     