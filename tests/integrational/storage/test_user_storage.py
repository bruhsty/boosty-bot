from datetime import datetime
from typing import AsyncIterable

import pytest
import pytest_asyncio
from integrational.utils import insert_user
from registration.adapters.storage import UserStorage
from registration.domain import models
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture(scope="function")
async def user_storage(session: AsyncSession) -> AsyncIterable[UserStorage]:
    storage = UserStorage(session)
    yield storage
    await storage.close()


@pytest.mark.asyncio
async def test_user_storage_can_add_user(user_storage: UserStorage):
    user = models.User(
        telegram_id=123,
        profiles=[
            models.BoostyProfile(
                id=246,
                name="John Doe",
                email="johndoe@example.com",
                next_pay_time=datetime(2077, 1, 1),
                banned=False,
                level=models.SubscriptionLevel(
                    id=745,
                    name="Level 1",
                    price=200,
                    is_archived=False,
                ),
                verification_codes=[],
            ),
        ],
    )

    await user_storage.add(user)
    returned_user = await user_storage.get(user.id)

    assert user.id == returned_user.id
    assert user.profiles == returned_user.profiles


@pytest.mark.asyncio
async def test_user_storage_can_retrieve_user_by_id(
    user_storage: UserStorage, session: AsyncSession
):
    await insert_user(session)
    await session.commit()
    user = await user_storage.get(12345678)
    assert user.id == 12345678
    profile = next(iter(user.profiles))
    assert profile.id == 123
    assert profile.level.id == 1
