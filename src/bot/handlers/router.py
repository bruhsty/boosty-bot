from aiogram import Router

from .dialogs import register_dialogs


async def on_startup():
    pass


async def on_shutdown():
    pass


def register_handlers(router: Router):
    register_dialogs(router)
    router.startup.register(on_startup)
    router.shutdown.register(on_shutdown)
