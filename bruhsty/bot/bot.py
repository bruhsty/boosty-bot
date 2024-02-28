import asyncio
from logging import Logger

import uvicorn
import aiogram
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from .handlers import register_handlers
from aiohttp import web

__all__ = ["BruhstyBot"]


class BruhstyBot:

    def __init__(
            self,
            token: str,
            logger: Logger,
            storage: BaseStorage | None = None,
    ) -> None:
        self.bot = aiogram.Bot(token)
        self.storage = storage or MemoryStorage()
        self.dp = aiogram.Dispatcher(storage=self.storage)
        self.logger = logger
        register_handlers(self.dp)

    async def register_webhook(
            self,
            url: str,
            max_connections: int = 40,
            drop_pending_updates: bool = True,
    ) -> None:
        await self.bot.set_webhook(
            url,
            max_connections=max_connections,
            drop_pending_updates=drop_pending_updates
        )

    def start_webhook(
            self,
            host: str = '127.0.0.1',
            port: int = 8080,
            secret_token: str | None = None,
            webhook_path: str = "/webhook",
            workers: int = 16,
    ) -> None:
        app = web.Application()
        handler = SimpleRequestHandler(self.dp, self.bot, secret_token=secret_token)
        handler.register(app, webhook_path)
        setup_application(app, self.dp)

        self.logger.info("start listening for webhook")
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=workers,
        )

    def start_polling(
            self,
            timeout: int = 10,
    ) -> None:
        self.logger.info("start polling", {"timeout": timeout})
        asyncio.run(self.dp.start_polling(self.bot, polling_timeout=timeout))
