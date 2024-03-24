import abc
from typing import Any, AsyncIterable, Generic, Protocol, Sequence, TypeVar

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from bruhsty.storage.specs import Specification

from .spec import spec_to_query

ID = TypeVar("ID")


class Model(Protocol[ID]):
    id: ID


class BaseSQLStorage(Generic[ID], abc.ABC):
    Select: Any

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.seen = set[Model[ID]]()

    async def add(self, model: Any) -> Any:
        schema = self._model_to_schema(model)
        self.session.add(schema)
        self.seen.add(model)
        return self._schema_to_model(schema)

    async def get_all(
        self,
        filter_: Specification,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[Any]:
        return [result async for result in self.get(filter_, limit, offset)]

    async def get(
        self,
        filter_: Specification,
        limit: int | None = None,
        offset: int | None = None,
    ) -> AsyncIterable[Any]:
        query = self._build_find_query(filter_, limit, offset)
        cursor = await self.session.stream_scalars(query)
        async for result in cursor:  # type: ignore
            yield self._schema_to_model(result)

    @abc.abstractmethod
    def _model_to_schema(self, model: Any) -> Any:
        pass

    @abc.abstractmethod
    def _schema_to_model(self, schema: Any) -> Any:
        pass

    @abc.abstractmethod
    def _resolve_name(self, name: str) -> Any:
        pass

    def _build_find_query(
        self,
        filter_: Specification,
        limit: int | None = None,
        offset: int | None = None,
    ) -> sa.Select:
        query: sa.Select = sa.Select(self.Select).where(spec_to_query(filter_, self._resolve_name))
        if limit is not None:
            query = query.limit(limit)

        if offset is not None:
            query = query.offset(offset)

        return query

    async def close(self) -> None:
        self.seen.clear()
