__all__ = ["register_commands"]

from aiogram import Router
from aiogram.filters import Command

from .start import start_command


def register_commands(router: Router):
    router.message.register(start_command, Command("start"))
