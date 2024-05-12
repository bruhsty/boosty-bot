import asyncio
import logging

import aiogram
import aiogram_dialog
import uvicorn
from aiogram.fsm.storage.base import BaseStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dependency_injector.wiring import Provide, inject

from .container import AppContainer
from .router import register_handlers

__all__ = ["BruhstyBot"]


class BruhstyBot:
    @inject
    def __init__(
        self,
        token: str = Provide[AppContainer.config.bot.token],
        storage: BaseStorage = Provide[AppContainer.state_storage],
    ) -> None:
        self.bot = aiogram.Bot(token)
        self.storage = storage
        self.dp = aiogram.Dispatcher(storage=self.storage)
        register_handlers(self.dp)
        aiogram_dialog.setup_dialogs(self.dp)

    async def register_webhook(
        self,
        url: str,
        max_connections: int = 40,
        drop_pending_updates: bool = True,
    ) -> None:
        await self.bot.set_webhook(
            url,
            max_connections=max_connections,
            drop_pending_updates=drop_pending_updates,
        )

    @inject
    def start_webhook(
        self,
        host: str = Provide[AppContainer.config.bot.webhook.host],
        port: int = Provide[AppContainer.config.bot.webhook.port],
        secret_token: str | None = Provide[AppContainer.config.bot.webhook.secret_token],
        webhook_path: str = Provide[AppContainer.config.bot.webhook.webhook_path],
        workers: int = Provide[AppContainer.config.bot.webhook.workers],
    ) -> None:
        app = web.Application()
        handler = SimpleRequestHandler(self.dp, self.bot, secret_token=secret_token)
        handler.register(app, webhook_path)
        setup_application(app, self.dp)

        logging.info("start listening for webhook")
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=workers,
        )

    def start_polling(
        self,
        timeout: int = 1,
    ) -> None:
        logging.info("start polling", {"timeout": timeout})
        asyncio.run(self.dp.start_polling(self.bot, polling_timeout=timeout))
