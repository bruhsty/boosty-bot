import abc
from typing import Any, AsyncIterable, AsyncIterator, Sequence, TypeVar

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.interfaces import ORMOption

from ..domain import Aggregate
from ..orm import Base
from .storage import AbstractStorage

TID = TypeVar("TID")
T = TypeVar("T")


class SQLStorage(AbstractStorage[TID]):
    db_model: Base
    load_options: Sequence[ORMOption] = []

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def add(self, item: Aggregate[TID]) -> None:
        self._seen(item)
        self.session.add(self._to_db_model(item))

    async def persist(self, item: Aggregate[TID]) -> None:
        self._seen(item)
        merged = await self.session.merge(
            self._to_db_model(item),
            options=self.load_options,
        )
        self.session.add(merged)

    async def get(self, item_id: TID) -> Aggregate[TID] | None:
        query = self._get_by_id_query(item_id)
        model = await one_or_none(self._find_all(query))
        if model:
            self._seen(model)
        return model

    async def _find_all(self, query) -> AsyncIterator[Aggregate[TID]]:
        result = await self.session.execute(query)
        for item in result.scalars().unique().all():
            domain_model = self._to_domain(item)
            self._seen(domain_model)
            yield domain_model

    @abc.abstractmethod
    def _to_domain(self, db_model: Any) -> Aggregate[TID]:
        pass

    @abc.abstractmethod
    def _to_db_model(self, item: Aggregate[TID]) -> Any:
        pass

    def _get_by_id_query(self, item_id: TID) -> Any:
        return (
            sa.Select(self.db_model).where(self.db_model.id == item_id).options(*self.load_options)
        )


async def one_or_none(iterable: AsyncIterable[T]) -> T | None:
    try:
        return await anext(aiter(iterable))
    except StopAsyncIteration:
        return None
