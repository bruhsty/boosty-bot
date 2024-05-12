from typing import AsyncIterable

import pytest
import pytest_asyncio
from integrational.utils import insert_user
from sqlalchemy.ext.asyncio import AsyncSession
from user.adapters.storage import UserStorage
from user.domain import models


@pytest_asyncio.fixture(scope="function")
async def user_storage(session: AsyncSession) -> AsyncIterable[UserStorage]:
    storage = UserStorage(session)
    yield storage
    await storage.close()


@pytest.mark.asyncio
async def test_user_storage_can_add_user(user_storage: UserStorage):
    user = models.User(
        telegram_id=123,
    )
    user.add_email(new_email="johndoe@example.com")

    await user_storage.add(user)
    returned_user = await user_storage.get(user.id)

    assert user.id == returned_user.id
    assert user.emails == returned_user.emails


@pytest.mark.asyncio
async def test_user_storage_can_retrieve_user_by_id(
    user_storage: UserStorage, session: AsyncSession
):
    await insert_user(session)
    await session.commit()
    user = await user_storage.get(12345678)
    assert user.id == 12345678
    email = next(iter(user.emails))
    assert email.email == "johndoe@example.com"
    assert email.verification_codes[0].value == "123-456"
