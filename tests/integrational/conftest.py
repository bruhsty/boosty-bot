import contextlib
from typing import AsyncIterable

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bruhsty import config
from bruhsty.storage.sql.base import Base


@contextlib.asynccontextmanager
async def connect(engine: AsyncEngine) -> AsyncIterable[AsyncConnection]:
    conn = await engine.connect()
    try:
        yield conn
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
    finally:
        await conn.close()


@pytest.fixture(scope="session")
def cfg() -> config.Config:
    return config.parse_file("config.test.yaml")


@pytest_asyncio.fixture(scope="function")
async def sa_engine(cfg: config.Config) -> AsyncEngine:
    db = cfg.database
    url = f"postgresql+asyncpg://{db.username}:{db.password}@{db.host}:{db.port}/{db.database}"
    engine = create_async_engine(url, echo=True, connect_args={"ssl": db.ssl_mode})

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose(close=True)


@pytest_asyncio.fixture(scope="function")
async def sessionmaker(sa_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(sa_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def session(sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncSession:
    async with sessionmaker() as session:
        yield session
        await session.rollback()
