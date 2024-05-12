import pytest
from common.domain import DomainEvent
from common.service_layer import AbstractMessageBus
from integrational.orm.test_user_schema import execute_text
from integrational.utils import insert_user
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from user.domain.events import VerificationCodeIssued
from user.domain.models import User
from user.service_layer.unit_of_work import UnitOfWork


class FakeMessageBus(AbstractMessageBus):
    def __init__(self) -> None:
        self.events = list[DomainEvent]()

    async def publish(self, *new_events: DomainEvent) -> None:
        self.events.extend(new_events)


class FakeUserStorage:
    def __init__(self) -> None:
        self.users = dict[int, User]()
        self.seen = set[User]()

    async def add(self, user: User) -> None:
        self.users[user.id] = user
        self.seen.add(user)

    async def get(self, user_id: int) -> User | None:
        if user_id not in self.users:
            return None

        user = self.users[user_id]
        self.seen.add(user)
        return user

    async def close(self) -> None:
        self.seen.clear()


@pytest.fixture(scope="function")
def message_bus() -> FakeMessageBus:
    return FakeMessageBus()


@pytest.fixture(scope="function")
def uow(sessionmaker: async_sessionmaker[AsyncSession], message_bus: FakeMessageBus) -> UnitOfWork:
    return UnitOfWork(
        bus=message_bus,
        sessionmaker=sessionmaker,
    )


@pytest.mark.asyncio
async def test_uow_rollbacks_not_commited_by_default(uow: UnitOfWork, session: AsyncSession):
    async with uow:
        await insert_user(uow.session)

    [[rows]] = await execute_text(session, "SELECT count(*) FROM users")
    assert rows == 0


@pytest.mark.asyncio
async def test_uow_commits_changed_data(uow: UnitOfWork):
    async with uow:
        user = User(123456)
        await uow.user_storage.add(user)
        await uow.commit()

        user = User(7689)
        await uow.user_storage.add(user)
        await uow.rollback()

    async with uow:
        user = await uow.user_storage.get(123456)
        assert user is not None

        user = await uow.user_storage.get(7689)
        assert user is None


@pytest.mark.asyncio
async def test_uow_collects_event_from_aggregates(uow: UnitOfWork, session: AsyncSession):
    await insert_user(session)
    await session.commit()

    async with uow:
        user = await uow.user_storage.get(12345678)

        user.add_email("johndoe1@example.com")
        await uow.commit()

    assert type(uow.bus.events[0]) is VerificationCodeIssued  # type: ignore
