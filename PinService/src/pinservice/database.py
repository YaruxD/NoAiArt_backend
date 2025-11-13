from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .settings import settings

DATABASE_URL = settings.DATABASE_URL_asyncpg

engine = create_async_engine(DATABASE_URL)

sessionmaker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_session():
    async with sessionmaker() as session:
        yield session
