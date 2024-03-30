from typing import cast

from common.service_layer import AbstractMessageBus, SQLUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from user.adapters import UserStorage


class UnitOfWork(SQLUnitOfWork):
    def __init__(
        self, bus: AbstractMessageBus, sessionmaker: async_sessionmaker[AsyncSession]
    ) -> None:
        super().__init__(bus, sessionmaker, [UserStorage])

    @property
    def user_storage(self) -> UserStorage:
        return cast(UserStorage, self.storages[0])
