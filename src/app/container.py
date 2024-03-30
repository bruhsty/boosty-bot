import argparse
import logging
import pathlib
import sys

import httpx
from aiogram.fsm.storage.memory import MemoryStorage
from common.adapters.boosty import BoostyAPI
from common.adapters.email import SMTPEmailService
from common.service_layer import MessageBus
from dependency_injector import providers, resources
from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from user.domain.events import VerificationCodeIssued
from user.service_layer import handlers
from user.service_layer.unit_of_work import UnitOfWork


class DBEngine(resources.Resource[AsyncEngine]):
    def init(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        database: str,
        sslmode: str,
    ) -> AsyncEngine:
        url = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
        return create_async_engine(url, echo=True, connect_args={"ssl": sslmode})

    async def shutdown(self, resource: AsyncEngine) -> None:
        pass


def parse_cli_args():
    parser = argparse.ArgumentParser(prog="bruhsty")
    parser.add_argument(
        "-c",
        "--config",
        type=pathlib.Path,
        default=pathlib.Path("./config/config.yaml"),
        help="path to config file",
    )
    return parser.parse_args(sys.argv[1:])


class AppContainer(DeclarativeContainer):
    wiring_config = WiringConfiguration(
        packages=[],
        modules=[
            ".router",
            ".bot",
            "registration.bot",
        ],
    )

    config = providers.Configuration()

    database_engine = providers.Resource(
        DBEngine,
        host=config.database.host,
        port=config.database.port,
        username=config.database.username,
        password=config.database.password,
        database=config.database.database,
        sslmode=config.database.sslmode,
    )

    sessionmaker = providers.Singleton[async_sessionmaker[AsyncSession]](
        async_sessionmaker,
        bind=database_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    session = providers.Factory[AsyncSession](sessionmaker)

    message_bus = providers.Singleton(
        MessageBus,
        event_handlers={
            VerificationCodeIssued: [handlers.send_verification_code],
        },
    )

    http_client = providers.Singleton(
        httpx.AsyncClient,
    )

    boosty_client = providers.Singleton(
        BoostyAPI,
        access_token=config.boosty.access_token,
        refresh_token=config.boosty.refresh_token,
        http_client=http_client,
    )

    state_storage = providers.Singleton(MemoryStorage)

    cli_args = providers.Singleton(parse_cli_args)

    logger = providers.Resource(
        logging.basicConfig,
        level=config.logger.level,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s: %(message)s",
    )

    unit_of_work = providers.Factory(
        UnitOfWork,
        bus=message_bus,
        sessionmaker=sessionmaker,
    )

    email_service = providers.Singleton(
        SMTPEmailService,
        server_host=config.smtp.host,
        server_port=config.smtp.port,
        username=config.smtp.username,
        password=config.smtp.password,
        use_tls=config.smtp.use_tls,
    )
