import typing
from typing import Any

from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button
from app.container import AppContainer
from boosty import BoostyProfileStorage
from dependency_injector.wiring import Provide, inject

from ..domain.models import Channel, EmailAlreadyAdded, InvalidCodeError
from ..service_layer import channels, register
from ..service_layer.unit_of_work import UnitOfWork
from .state import MenuStatesGroup

__all__ = [
    "menu",
    "add_email",
    "list_emails",
    "on_email_selected",
    "remove_email",
    "go_back",
    "email_validate",
    "email_resend_code",
    "get_email_list",
    "on_input_verification_code",
    "switch_window",
    "list_channels",
]


@inject
async def menu(
    msg: Message,
    dialog_manager: DialogManager,
):
    # await msg.bot.approve_chat_join_request(-1001994271159, 1195647957)
    await dialog_manager.start(MenuStatesGroup.main, mode=StartMode.RESET_STACK)


class WindowSwitcher(typing.Protocol):
    @typing.overload
    async def __call__(self, cb: CallbackQuery, button: Button, manager: DialogManager) -> None: ...

    async def __call__(self, *args, **kwargs) -> None: ...


def switch_window(new_state: State, reset_stack: bool = False) -> WindowSwitcher:
    async def switcher(*args, **kwargs) -> None:
        manager: DialogManager = args[2]
        if reset_stack:
            await manager.reset_stack()
        return await manager.switch_to(new_state)

    return switcher


@inject
async def email_validate(
    msg: Message,
    widget: ManagedTextInput,
    manager: DialogManager,
    email: str,
    uow: UnitOfWork = Provide[AppContainer.unit_of_work],
) -> None:
    if "verifying_email" in manager.dialog_data:
        del manager.dialog_data["verifying_email"]

    try:
        await register.add_email(msg.from_user.id, email, uow)
    except EmailAlreadyAdded:
        return await manager.switch_to(MenuStatesGroup.invalid_email_value)

    manager.dialog_data["verifying_email"] = email
    await manager.switch_to(MenuStatesGroup.email_verify)


@inject
async def email_resend_code(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    uow: UnitOfWork = Provide[AppContainer.unit_of_work],
) -> None:
    email = manager.dialog_data["selected_email"]["email"]
    manager.dialog_data["verifying_email"] = email
    await register.resend_code(callback.from_user.id, email, uow)
    await manager.switch_to(MenuStatesGroup.email_verify)


async def on_email_input_error(
    msg: Message,
    widget: ManagedTextInput,
    manager: DialogManager,
    value: str,
) -> None:
    await manager.switch_to(MenuStatesGroup.invalid_email_value)


async def add_email(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    await manager.switch_to(MenuStatesGroup.email_add)


@inject
async def list_emails(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    uow: UnitOfWork = Provide[AppContainer.unit_of_work],
    **kwargs,
) -> None:
    user = await register.get_or_create_user(callback.from_user.id, uow)
    emails = [{"email": e.email, "is_verified": e.is_verified} for e in user.emails]
    manager.dialog_data["emails"] = emails
    await manager.switch_to(MenuStatesGroup.email_list)


async def on_email_selected(
    callback: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    item: str,
):
    email = next(email for email in manager.dialog_data["emails"] if email["email"] == item)
    manager.dialog_data["selected_email"] = email
    await manager.switch_to(MenuStatesGroup.email_settings)


@inject
async def remove_email(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    uow: UnitOfWork = Provide[AppContainer.unit_of_work],
) -> None:
    telegram_id = callback.from_user.id
    email = manager.dialog_data["selected_email"]["email"]
    await register.remove_email(telegram_id, email, uow)
    await manager.switch_to(MenuStatesGroup.main)


@inject
async def on_input_verification_code(
    msg: Message,
    widget: ManagedTextInput,
    manager: DialogManager,
    code: str,
    uow: UnitOfWork = Provide[AppContainer.unit_of_work],
) -> None:
    telegram_id = msg.from_user.id
    email = manager.dialog_data["verifying_email"]
    try:
        await register.confirm_email(telegram_id, email, code, uow)
        await manager.switch_to(MenuStatesGroup.main)
    except InvalidCodeError:
        await manager.switch_to(MenuStatesGroup.invalid_code)


@inject
async def list_channels(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    all_channels: list[dict] = Provide[AppContainer.config.bot.channels],
    storage: BoostyProfileStorage = Provide[AppContainer.boosty_storage],
    uow: UnitOfWork = Provide[AppContainer.unit_of_work],
) -> None:
    accessible_channels = await channels.list_channels(
        callback.from_user.id, all_channels, storage, uow
    )

    def channel_to_view(channel: Channel) -> dict:
        return {
            "id": channel.id,
            "invite_link": channel.invite_link,
            "level_name": channel.level.name,
        }

    manager.dialog_data["channels"] = [channel_to_view(c) for c in accessible_channels]

    if accessible_channels:
        await manager.switch_to(MenuStatesGroup.channels_list)
    else:
        await manager.switch_to(MenuStatesGroup.channels_list_not_available)


async def go_back(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    await manager.back()


async def get_email_list(
    dialog_manager: DialogManager,
    **kwargs,
) -> dict[str, Any]:
    return dialog_manager.dialog_data
