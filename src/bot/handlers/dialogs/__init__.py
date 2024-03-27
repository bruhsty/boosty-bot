from aiogram import Router

from . import menu


def register_dialogs(router: Router):
    menu.register_dialog(router)
