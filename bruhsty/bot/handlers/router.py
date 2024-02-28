from aiogram import Router

from .commands import register_commands


async def on_startup():
    pass


async def on_shutdown():
    pass


def register_handlers(router: Router):
    register_commands(router)
    router.startup.register(on_startup)
    router.shutdown.register(on_shutdown)
