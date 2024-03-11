import contextlib

from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

__all__ = ["metadata", "Base", "connect"]

metadata = MetaData()


class Base(AsyncAttrs, DeclarativeBase):
    ...


@contextlib.asynccontextmanager
async def connect(db_dsn: str) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(db_dsn, echo=True)
    try:
        session_maker = async_sessionmaker(engine, expire_on_commit=False)
        yield session_maker
    finally:
        await engine.dispose()
