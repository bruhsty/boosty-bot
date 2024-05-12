import abc
from typing import Generic, Iterable, TypeVar

from common.domain import Aggregate, DomainEvent

TID = TypeVar("TID")


class AbstractStorage(abc.ABC, Generic[TID]):
    @abc.abstractmethod
    async def add(self, obj: Aggregate[TID]) -> None: ...

    @abc.abstractmethod
    async def get(self, obj: TID) -> Aggregate[TID]: ...

    @abc.abstractmethod
    async def collect_events(self) -> Iterable[DomainEvent]: ...
