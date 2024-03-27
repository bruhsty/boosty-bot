from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

__all__ = [
    "menu",
    "add_email",
    "list_emails",
    "on_email_selected",
    "remove_email",
    "cancel_email_input",
    "go_back",
]

from .state import MenuStatesGroup


async def menu(msg: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MenuStatesGroup.main)


async def add_email(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    await manager.switch_to(MenuStatesGroup.email_add)


async def list_emails(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    await manager.switch_to(MenuStatesGroup.email_list)


async def on_email_selected(
    callback: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    item: str,
):
    await manager.switch_to(MenuStatesGroup.email_settings)


async def remove_email(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    print("remove email")


async def cancel_email_input(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    await manager.switch_to(MenuStatesGroup.main)


async def go_back(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    await manager.back()


async def test_getter(*args, **kwargs):
    print(args, kwargs)
    return {
        "selected_email": "johndoe@example.com",
        "emails": [
            {"email": "johndoe@example.com"},
            {"email": "alaexsmith@example.com"},
        ],
    }
