from typing import cast

from common.service_layer import MessageBus, SQLUnitOfWork
from registration.adapters import UserStorage
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class UnitOfWork(SQLUnitOfWork):
    def __init__(self, bus: MessageBus, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(bus, sessionmaker, [UserStorage])

    @property
    def user_storage(self) -> UserStorage:
        return cast(UserStorage, self.storages[0])
