import logging

import aiogram
from aiogram.types import ChatJoinRequest
from app.container import AppContainer
from boosty import BoostyProfileStorage
from dependency_injector.wiring import Provide, inject
from user.bot import get_or_create_user
from user.domain.models import User
from user.service_layer.unit_of_work import UnitOfWork

from channel.service_layer import can_access_channel
from config import Channel

logger = logging.getLogger(__name__)


def register_handlers(router: aiogram.Router) -> None:
    router.chat_join_request.outer_middleware.register(get_or_create_user)
    router.chat_join_request.register(on_chat_join_request)


@inject
async def on_chat_join_request(
    req: ChatJoinRequest,
    channels: list[Channel] = Provide[AppContainer.config.bot.channels],
    profile_storage: BoostyProfileStorage = Provide[AppContainer.boosty_storage],
    uow: UnitOfWork = Provide[AppContainer.unit_of_work],
) -> None:
    logging.info(f"Got chat join request from {req.from_user.id}")
    async with uow:
        channel = next((c for c in channels if c["id"] == req.chat.id), None)
        if channel is None:
            return

        user: User | None = await uow.user_storage.get(req.from_user.id)

        if await can_access_channel(user, profile_storage, channel):
            logging.info(
                f"Approved chat join request from " f"{req.from_user.id} to channel {req.chat.id}"
            )
            await req.approve()
        else:
            logging.info(
                f"Declined chat join request from " f"{req.from_user.id} to channel {req.chat.id}"
            )
            await req.decline()
