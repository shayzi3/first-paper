from contextlib import asynccontextmanager

from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship, Mapped
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import ForeignKey, Integer, URL




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



class Item(Base):
    __tablename__ = "items"

    short_name: Mapped[str] = mapped_column(primary_key=True)
    
    wears: Mapped[list["ItemWear"]] = relationship(back_populates="item")
    collections: Mapped[list["ItemCollection"]] = relationship(back_populates="item")


class ItemWear(Base):
     __tablename__ = "items_wears"
     
     id: Mapped[int] = mapped_column(Integer, primary_key=True)
     short_name: Mapped[int] = mapped_column(ForeignKey("items.short_name"))
     hash_name: Mapped[str] = mapped_column()
     
     item: Mapped["Item"] = relationship(back_populates="wears")
     
     
class ItemCollection(Base):
     __tablename__ = "items_collections"
     
     id: Mapped[int] = mapped_column(Integer, primary_key=True)
     short_name: Mapped[int] = mapped_column(ForeignKey("items.short_name"))
     collection: Mapped[str] = mapped_column()
     
     item: Mapped["Item"] = relationship(back_populates="collections")
     
     
eng = create_async_engine(
     url=URL.create(
          drivername="postgresql+asyncpg",
          username="postgres",
          password="193wVLAD127#!",
          host="127.0.0.1",
          port=5432,
          database="testing"
     ).render_as_string(hide_password=False),
     echo=True
)
session_maker = async_sessionmaker(eng)


@asynccontextmanager
async def session():
     async with session_maker() as session:
          yield session