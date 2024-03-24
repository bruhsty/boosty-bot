import abc
from typing import Callable, Generic, Iterable, Protocol, Self, TypeVar, cast

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bruhsty.domain import events
from bruhsty.storage.user.postgres import UserStorage

TID = TypeVar("TID")


class Model(Generic[TID]):
    id: TID


class Repository(Protocol[TID]):
    async def add(self, obj: Model[TID]) -> None: ...

    async def get(self, obj: TID) -> Model[TID]: ...

    async def collect_events(self) -> Iterable[events.Event]: ...


class MessageBus(Protocol):
    async def publish(self, *new_events: events.Event) -> None: ...


class UnitOfWorkError(Exception):
    pass


class AbstractUnitOfWork(abc.ABC):
    repositories: list[Repository]

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

    async def publish_events(self) -> Iterable[events.Event]:
        all_events = list[events.Event]()
        for repo in self.repositories:
            all_events.extend(await repo.collect_events())

        all_events.sort(key=lambda event: event.time)
        return all_events

    @abc.abstractmethod
    async def _publish_events(self, new_events: Iterable[events.Event]) -> None:
        pass


class SQLUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        bus: MessageBus,
        sessionmaker: async_sessionmaker[AsyncSession],
        repo_factories: list[Callable[[AsyncSession], Repository]],
    ) -> None:
        self.bus = bus
        self.repo_factories = repo_factories
        self.repositories = list[Repository]()
        self.sessionmaker = sessionmaker
        self.session: AsyncSession | None = None

    def _init_repositories(self) -> None:
        for maker in self.repo_factories:
            self.repositories.append(maker(self.session))

    def _dispose_repositories(self) -> None:
        self.repositories = []

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

    async def _publish_events(self, new_events: Iterable[events.Event]) -> None:
        await self.bus.publish(*new_events)


class UserUnitOfWork(SQLUnitOfWork):
    def __init__(self, bus: MessageBus, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(bus, sessionmaker, [UserStorage])

    @property
    def user_storage(self) -> UserStorage:
        return cast(UserStorage, self.repositories[0])
