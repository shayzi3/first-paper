from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.config import config


engine = create_async_engine(
     url=config.build_sqlalchemy_url(),
     echo=config.echo
)
sessionmaker = async_sessionmaker(engine)

async def async_session():
     async with sessionmaker() as session:
          yield session

