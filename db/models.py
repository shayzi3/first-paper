from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import ForeignKey, BigInteger, insert

from .session import async_session
from .test_data import users, items, market_items





class Base(DeclarativeBase, AsyncAttrs):
     _cached_orm_models: dict[str, type["Base"]] = {}

     @classmethod
     def orm_models(cls) -> dict[str, type["Base"]]:
          if not cls._cached_orm_models:
               models = {}
               for mapper in cls.registry.mappers:
                    models[mapper.class_.__tablename__] = mapper.class_
               cls._cached_orm_models.update(models)
          return cls._cached_orm_models
     

class User(Base):
     __tablename__ = "users"
     
     id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
     username: Mapped[str] = mapped_column(nullable=False)
     
     sell_items: Mapped[list["MarketItem"]] = relationship(back_populates="user")
     
     
class Item(Base):
     __tablename__ = "items"
     
     id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
     short_name: Mapped[str] = mapped_column(nullable=False)
     category: Mapped[str] = mapped_column(nullable=False)
     
     market_items: Mapped[list["MarketItem"]] = relationship(back_populates="item")
     

class MarketItem(Base):
     __tablename__ = "market_items"
     
     id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
     user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"))
     item_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("items.id", ondelete="CASCADE", onupdate="CASCADE"))
     full_name: Mapped[str] = mapped_column(nullable=False)
     wear: Mapped[str] = mapped_column(nullable=False)
     price: Mapped[float] = mapped_column(nullable=False)
     
     item: Mapped["Item"] = relationship(back_populates="market_items")
     user: Mapped["User"] = relationship(back_populates="sell_items")
     
     
     
async def create_test_data() -> None:
     tables = [(User, users), (Item, items), (MarketItem, market_items)]
     async with async_session() as session:
          for table, values in tables:
               query = insert(table).values(values)
               await session.execute(query)
          await session.commit()