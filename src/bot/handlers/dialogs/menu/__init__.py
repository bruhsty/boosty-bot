from aiogram import Router
from aiogram.filters import Command

from .dialog import menu_dialog
from .handlers import menu
from .state import MenuStatesGroup

__all__ = ["MenuStatesGroup", "menu_dialog"]


def register_dialog(router: Router) -> None:
    router.include_router(menu_dialog)
    router.message.register(menu, Command("menu"))
