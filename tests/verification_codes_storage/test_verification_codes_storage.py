import asyncio
import dataclasses

import pytest_asyncio
import sqlalchemy as sa
from datetime import timedelta, datetime

import faker
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from bruhsty.storage.verification_codes.postgres import CodeStorage
from bruhsty.storage.verification_codes import Code
from bruhsty.storage.verification_codes.postgres import VerificationCode


@pytest.fixture(scope='function')
def unused_code(fake: faker.Faker) -> Code:
    now = datetime.now()
    return Code(
        code_id=0,
        code=str(fake.pyint(min_value=0, max_value=999_999)),
        valid_until=now + timedelta(minutes=10),
        used_at=None,
        created_at=now - timedelta(minutes=1),
        telegram_id=fake.pyint(min_value=100_000, max_value=10_000_000),
        email=fake.email(),
    )


@pytest_asyncio.fixture(scope='function')
async def empty_store(sessionmaker):
    storage = CodeStorage(sessionmaker, timedelta(minutes=10))
    yield storage
    await storage.close()


@pytest_asyncio.fixture(scope='function')
async def store_with_data(empty_store, fake):
    async def insert():
        telegram_id = fake.pyint(min_value=100_000, max_value=10_000_000)
        email = fake.email()
        code = str(fake.pyint(min_value=0, max_value=999_999))
        await empty_store.add(telegram_id, email, code)

    await asyncio.gather(*[insert() for _ in range(100)])


@pytest.mark.asyncio
async def test_add_code(empty_store, sessionmaker, unused_code: Code):
    saved_code = await empty_store.add(unused_code.telegram_id, unused_code.email, unused_code.code)

    expected = dataclasses.replace(unused_code, code_id=saved_code.code_id)

    assert_codes_equal(expected, saved_code)

    async with sessionmaker() as session:
        session: AsyncSession
        code = (await session.scalar(
            sa.select(VerificationCode).
            where(VerificationCode.code_id == saved_code.code_id)
        ))

        assert_codes_equal(expected, code.to_model())


@pytest.mark.asyncio
async def test_find_by_id(empty_store, unused_code):
    saved = await empty_store.add(unused_code.telegram_id, unused_code.email, unused_code.code)

    actual = [c async for c in empty_store.find(Code.code_id == saved.code_id)]
    assert [saved] == actual


@pytest.mark.asyncio
def assert_codes_equal(expected: Code, actual: Code) -> None:
    assert expected.code_id == actual.code_id, "code_id must be equal"
    assert expected.code == actual.code, "code must be equal"
    assert expected.email == actual.email, "email must be equal"

    if expected.used_at is not None or actual.used_at is not None:
        assert expected.used_at - actual.used_at < timedelta(seconds=1), "used_at must be equal"
    else:
        assert expected.used_at == actual.used_at, "used_at must be equal"

    assert expected.telegram_id == actual.telegram_id, "telegram_id must be equal"
    assert expected.valid_until - actual.valid_until < timedelta(seconds=1), "valid_until must be equal"
    assert expected.created_at - actual.created_at < timedelta(seconds=1), "created_at must be equal"
