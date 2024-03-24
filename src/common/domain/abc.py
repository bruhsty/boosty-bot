from collections import deque
from typing import Generic, Sequence, TypeVar

from .events import DomainEvent

ID = TypeVar("ID")


class Aggregate(Generic[ID]):
    def __init__(self, id_: ID) -> None:
        self._id = id_
        self._events = deque[DomainEvent]()

    @property
    def id(self):
        return self._id

    def _push_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def pop_event(self) -> DomainEvent | None:
        return self._events.pop() if self._events else None

    def pop_all_events(self) -> Sequence[DomainEvent]:
        all_events = tuple(self._events)
        self._events.clear()
        return all_events
