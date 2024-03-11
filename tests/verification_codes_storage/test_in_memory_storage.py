from datetime import timedelta

import pytest
import pytest_asyncio

from bruhsty.storage.verification_codes.in_memory import CodeStorage


@pytest_asyncio.fixture(scope='function')
async def empty_storage():
    return CodeStorage(timedelta(minutes=10))


@pytest.mark.asyncio
async def test_add(empty_storage: CodeStorage):
    telegram_id = 1
    email = "email@example.com"
    code = "123456"

    code = await empty_storage.add(telegram_id, email, code)

    assert code.code == code
    assert code.code_id == 1
    assert code.used_at is None
    assert code.valid_until - code.created_at == timedelta(minutes=10)
