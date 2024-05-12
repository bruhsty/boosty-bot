from typing import Any, Awaitable, Callable, Dict

from aiogram.types import Update
from dependency_injector.wiring import Provide, inject

from user.service_layer import register
from user.service_layer.unit_of_work import UnitOfWork


@inject
async def get_or_create_user(
    handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: dict[str, Any],
    uow: UnitOfWork = Provide["unit_of_work"],
) -> Any:
    user = await register.get_or_create_user(event.from_user.id, uow)
    data["user"] = user
    return await handler(event, data)
