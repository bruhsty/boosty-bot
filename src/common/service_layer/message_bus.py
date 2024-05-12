import abc
from typing import Any, Awaitable, Callable, Coroutine, Sequence, Type

from common.domain import DomainEvent, events

EventHandler = Callable[[DomainEvent], Awaitable[None] | Coroutine[Any, Any, None]]


class AbstractMessageBus(abc.ABC):
    @abc.abstractmethod
    async def publish(self, *new_events: events.DomainEvent) -> None: ...


class MessageBus(AbstractMessageBus):
    def __init__(
        self,
        event_handlers: dict[Type[DomainEvent], Sequence[EventHandler]],
    ) -> None:
        self.event_handlers = event_handlers

    async def handle(self, event: DomainEvent) -> None:
        for handler in self.event_handlers.get(type(event), []):
            await handler(event)

    async def publish(self, *new_events: events.DomainEvent) -> None:
        for event in new_events:
            await self.handle(event)
