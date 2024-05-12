from common.service_layer import AbstractMessageBus
from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from user.service_layer.unit_of_work import UnitOfWork


class RegistrationContainer(DeclarativeContainer):
    message_bus = providers.Dependency[AbstractMessageBus]()
    sessionmaker = providers.Dependency[async_sessionmaker[AsyncSession]]()

    unit_of_work = providers.Factory(
        UnitOfWork,
        bus=message_bus,
        sessionmaker=sessionmaker,
    )
