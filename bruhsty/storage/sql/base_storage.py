import abc
from typing import Sequence, AsyncIterable, Any, Type
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from bruhsty.storage.specs import Specification
from .errors import NoRowAffectedError
from .spec import spec_to_query


class BaseSQLStorage(abc.ABC):
    Schema: Type
    ModelCreate: Type
    ModelGet: Type
    ModelUpdate: Type

    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self.sessionmaker = sessionmaker

    async def create(self, model: Any) -> Any:
        async with self.sessionmaker() as session:
            schema = self.model_to_schema(model)
            session.add(schema)
            return self.schema_to_model(schema)

    async def find_all(
            self,
            filter_: Specification,
            limit: int | None = None,
            offset: int | None = None,
    ) -> Sequence[Any]:
        return [result async for result in self.find(filter_, limit, offset)]

    async def find(
            self,
            filter_: Specification,
            limit: int | None = None,
            offset: int | None = None,
    ) -> AsyncIterable[Any]:
        async with self.sessionmaker() as session:
            query = self._build_find_query(filter_, limit, offset)
            cursor = await session.stream_scalars(query)
            async for result in cursor:  # type: ignore
                yield self.schema_to_model(result)

    async def update(
            self,
            filter_: Specification,
            **updates: Any,
    ) -> None:
        async with self.sessionmaker() as session:
            query = self._build_update_query(filter_, **updates)
            result = await session.execute(query)
        if result.rowcount == 0:
            raise NoRowAffectedError("No one row was affected by update query")

    async def delete(
            self,
            filter_: Specification
    ) -> None:
        async with self.sessionmaker() as session:
            query = self._build_delete_query(filter_)
            result = await session.execute(query)
        if result.rowcount == 0:
            raise NoRowAffectedError("No one row was affected by delete query")

    @abc.abstractmethod
    def model_to_schema(self, model: Any) -> Any:
        pass

    @abc.abstractmethod
    def schema_to_model(self, schema: Any) -> Any:
        pass

    @abc.abstractmethod
    def resolve_name(self, name: str) -> Any:
        pass

    def _build_find_query(
            self,
            filter_: Specification,
            limit: int | None = None,
            offset: int | None = None,
    ) -> sa.Select:
        query: sa.Select = (
            sa.Select(self.Schema)
            .where(spec_to_query(filter_, self.resolve_name))
        )
        if limit is not None:
            query = query.limit(limit)

        if offset is not None:
            query = query.offset(offset)

        return query

    def _build_update_query(self, filter_: Specification, **updates: Any) -> sa.Update:
        return (
            sa.update(self.Schema)
            .where(spec_to_query(filter_, self.resolve_name))
            .values(**updates)
        )

    def _build_delete_query(self, filter_: Specification) -> sa.Delete:
        return (
            sa.delete(self.Schema)
            .where(spec_to_query(filter_, self.resolve_name))
        )
