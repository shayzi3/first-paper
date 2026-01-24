from typing_extensions import Self
from sqlalchemy.ext.asyncio import AsyncSession

from repository.impl.alchemy import SQLAlchemyRepository
from db.session import sessionmaker
from db.models import User, Item, MarketItem
from schema.dto import UserDTO, ItemDTO, MarketItemDTO




class UnitOfWorkSQLAlchemy:
     
     def __init__(self) -> None:
          self._sessionmaker = sessionmaker
          self._session: AsyncSession | None = None
          self._cached_repository: dict[str, SQLAlchemyRepository] = {}
          
     async def __aenter__(self) -> Self:
          if self._session is None:
               self._session = self._sessionmaker()
          return self
     
     async def __aexit__(self, *args) -> None:
          if args[0]:
               await self.rollback()
          await self.close(*args)
          
     async def rollback(self) -> None:
          if self._session:
               await self._session.rollback()
               
     async def close(self, *args) -> None:
          if self._session:
               await self._session.__aexit__(*args)
               self._session = None
               self._cached_repository.clear()
               
     @property
     def user(self) -> SQLAlchemyRepository[UserDTO]:
          if self._session:
               cache_key = "user_repo"

               if cache_key not in self._cached_repository.keys():
                    self._cached_repository[cache_key] = SQLAlchemyRepository(session=self._session, model=User)
               return self._cached_repository[cache_key]
          raise ValueError("session don't found. call __aenter__")
     
     @property
     def item(self) -> SQLAlchemyRepository[ItemDTO]:
          if self._session:
               cache_key = "item_repo"
               
               if cache_key not in self._cached_repository.keys():
                    self._cached_repository[cache_key] = SQLAlchemyRepository(session=self._session, model=Item)
               return self._cached_repository[cache_key]
          raise ValueError("session don't found. call __aenter__")
     
     @property
     def market_item(self) -> SQLAlchemyRepository[MarketItemDTO]:
          if self._session:
               cache_key = "market_item_repo"
               
               if cache_key not in self._cached_repository.keys():
                    self._cached_repository[cache_key] = SQLAlchemyRepository(session=self._session, model=MarketItem)
               return self._cached_repository[cache_key]
          raise ValueError("session don't found. call __aenter__")
          