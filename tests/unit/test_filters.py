import pytest
from aiogram_tests.types.dataset import CALLBACK_QUERY, MESSAGE, UPDATE, USER
from common.bot.filters import is_admin

from config import Admin


@pytest.mark.asyncio
async def test_is_admin_filter_returns_True_if_user_in_admin_list_MESSAGE():
    update = UPDATE.as_object(
        message=MESSAGE.as_object(**{"text": "Hello, bot", "from": USER.as_object(id=3)})
    )
    result = await is_admin(
        update, [Admin(id=1), Admin(id=2), Admin(id=3), Admin(id=4), Admin(id=5)]
    )
    assert result is True


@pytest.mark.asyncio
async def test_is_admin_filter_returns_False_if_user_not_in_admin_list_MESSAGE():
    update = UPDATE.as_object(
        message=MESSAGE.as_object(**{"text": "Hello, bot", "from": USER.as_object(id=6)})
    )
    result = await is_admin(
        update, [Admin(id=1), Admin(id=2), Admin(id=3), Admin(id=4), Admin(id=5)]
    )
    assert result is False


@pytest.mark.asyncio
async def test_is_admin_filter_returns_True_if_user_in_admin_list_callback_query():
    update = UPDATE.as_object(
        callback_query=CALLBACK_QUERY.as_object(**{"id": "3", "from": USER.as_object(id=3)})
    )
    result = await is_admin(
        update, [Admin(id=1), Admin(id=2), Admin(id=3), Admin(id=4), Admin(id=5)]
    )
    assert result is True


@pytest.mark.asyncio
async def test_is_admin_filter_returns_False_if_user_not_in_admin_list_callback_query():
    update = UPDATE.as_object(
        callback_query=CALLBACK_QUERY.as_object(**{"id": "6", "from": USER.as_object(id=6)})
    )
    result = await is_admin(
        update, [Admin(id=1), Admin(id=2), Admin(id=3), Admin(id=4), Admin(id=5)]
    )
    assert result is False
