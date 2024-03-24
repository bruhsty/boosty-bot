import abc
from typing import Callable, Generic, Iterable, Protocol, Self, TypeVar

from common.adapters.storage import AbstractStorage
from common.domain import events
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

TID = TypeVar("TID")


class Model(Generic[TID]):
    id: TID


class MessageBus(Protocol):
    async def publish(self, *new_events: events.DomainEvent) -> None: ...


class UnitOfWorkError(Exception):
    pass


class AbstractUnitOfWork(abc.ABC):
    storages: list[AbstractStorage]

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_val is not None:
            await self.rollback()

    @abc.abstractmethod
    async def commit(self) -> None:
        pass

    @abc.abstractmethod
    async def rollback(self) -> None:
        pass

    async def publish_events(self) -> Iterable[events.DomainEvent]:
        all_events = list[events.DomainEvent]()
        for repo in self.storages:
            all_events.extend(await repo.collect_events())

        all_events.sort(key=lambda event: event.time)
        return all_events

    @abc.abstractmethod
    async def _publish_events(self, new_events: Iterable[events.DomainEvent]) -> None:
        pass


class SQLUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        bus: MessageBus,
        sessionmaker: async_sessionmaker[AsyncSession],
        storage_factories: list[Callable[[AsyncSession], AbstractStorage]],
    ) -> None:
        self.bus = bus
        self.storage_factories = storage_factories
        self.storages = list[AbstractStorage]()
        self.sessionmaker = sessionmaker
        self.session: AsyncSession | None = None

    def _init_repositories(self) -> None:
        for factory in self.storage_factories:
            self.storages.append(factory(self.session))

    def _dispose_repositories(self) -> None:
        self.storages = []

    async def __aenter__(self) -> Self:
        if self.session is not None:
            raise UnitOfWorkError("Can't begin new session until previous one is not finished")

        self.session = self.sessionmaker()
        await self.session.begin()
        self._init_repositories()
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session is None:
            raise UnitOfWorkError("Can't finish not started session. Maybe a race condition")

        await self.rollback()
        self._dispose_repositories()

        await self.session.close()

        result = await super().__aexit__(exc_type, exc_val, exc_tb)
        self.session = None
        return result

    async def commit(self) -> None:
        if self.session is None:
            raise UnitOfWorkError("Can't commit not started session")
        await self.session.commit()
        await self.bus.publish(*(await self.publish_events()))

    async def rollback(self) -> None:
        if self.session is None:
            raise UnitOfWorkError("Can't rollback not started session")
        await self.session.rollback()

    async def _publish_events(self, new_events: Iterable[events.DomainEvent]) -> None:
        await self.bus.publish(*new_events)
