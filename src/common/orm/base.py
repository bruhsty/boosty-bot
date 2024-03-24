import contextlib
from typing import AsyncIterator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

__all__ = ["metadata", "Base", "connect"]

metadata = MetaData()


class Base(AsyncAttrs, DeclarativeBase): ...


@contextlib.asynccontextmanager
async def connect(db_dsn: str) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(db_dsn, echo=True)
    try:
        session_maker = async_sessionmaker(engine, expire_on_commit=False)
        yield session_maker
    finally:
        await engine.dispose()
