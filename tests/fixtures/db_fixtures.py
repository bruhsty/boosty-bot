import pathlib

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncEngine,
    async_sessionmaker, AsyncSession
)
from bruhsty.storage.sql.base import metadata, Base

__all__ = ["sa_engine", "sessionmaker", "session"]


@pytest_asyncio.fixture()
async def sa_engine(tmp_path: pathlib.Path) -> AsyncEngine:
    path = tmp_path / "db.sqlite"
    engine = create_async_engine(f"sqlite+aiosqlite:///{path}", echo=True)
    yield engine
    await engine.dispose(close=True)


@pytest_asyncio.fixture(scope="function")
async def sessionmaker(sa_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    sessionmaker = async_sessionmaker(sa_engine, expire_on_commit=False)

    async with sa_engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield sessionmaker

    async with sa_engine.connect() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def session(sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncSession:
    async with sessionmaker() as session:
        yield session
