import aiogram
from aiogram.filters import Command

from .dialog import menu_dialog
from .handlers import menu
from .middlewares import get_or_create_user


def register_dialogs(router: aiogram.Router):
    router.message.outer_middleware()(get_or_create_user)
    router.message.register(menu, Command("menu"))
    router.include_router(menu_dialog)
