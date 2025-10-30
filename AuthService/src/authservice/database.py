from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .settings import settings

DATABASE_URL =  settings.DATABASE_URL_asyncpg

engine = create_async_engine(DATABASE_URL)

sessionmaker = async_sessionmaker(
    bind = engine,
    expire_on_commit = False,
)

async def get_session():
    async with sessionmaker() as session:
        yield session