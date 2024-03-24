import datetime
from collections import deque
from typing import Generic, Protocol, Sequence, TypeVar

ID = TypeVar("ID")


class Event(Protocol):
    time: datetime.datetime


class Aggregate(Generic[ID]):
    def __init__(self, id_: ID) -> None:
        self._id = id_
        self._events = deque[Event]()

    @property
    def id(self):
        return self._id

    def _push_event(self, event: Event) -> None:
        self._events.append(event)

    def pop_event(self) -> Event | None:
        return self._events.pop() if self._events else None

    def pop_all_events(self) -> Sequence[Event]:
        all_events = tuple(self._events)
        self._events.clear()
        return all_events
