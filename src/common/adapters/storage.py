import abc
from typing import Generic, Iterable, TypeVar

from common.domain import Aggregate, DomainEvent

TID = TypeVar("TID")


class AbstractStorage(abc.ABC, Generic[TID]):
    def __init__(self) -> None:
        self.__seen = set[Aggregate[TID]]()

    @abc.abstractmethod
    async def add(self, obj: Aggregate[TID]) -> None: ...

    @abc.abstractmethod
    async def get(self, obj: TID) -> Aggregate[TID]: ...

    def _seen(self, item: Aggregate[TID]) -> None:
        self.__seen.add(item)

    async def collect_events(self) -> Iterable[DomainEvent]:
        events = list[DomainEvent]()
        for item in self.__seen:
            event: DomainEvent
            while event := item.pop_event():
                events.append(event)

        events.sort(key=lambda e: e.time)
        return events
