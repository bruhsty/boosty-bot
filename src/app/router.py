import channel
import user
from aiogram import Router


async def on_startup():
    pass


async def on_shutdown():
    pass


def register_handlers(router: Router):
    user.bot.register_dialogs(router)
    channel.bot.register_handlers(router)
    router.startup.register(on_startup)
    router.shutdown.register(on_shutdown)
