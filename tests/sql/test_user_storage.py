import pytest
import pytest_asyncio

from bruhsty.storage.user.postgres import UserStorage
from bruhsty.storage.user.models import User


@pytest_asyncio.fixture(scope="function")
async def empty_user_storage(sessionmaker):
    return UserStorage(sessionmaker)


@pytest.mark.asyncio
async def test_build_find_query(empty_user_storage: UserStorage):
    actual_query = str(empty_user_storage._build_find_query(
        (User.email == "email@example.com") & (User.telegram_id == 123),
        limit=100,
        offset=2000,
    ))

    expected_query = ("SELECT users.telegram_id, users.email, users.is_verified \n"
                      "FROM users \n"
                      "WHERE users.email = :email_1 AND users.telegram_id = :telegram_id_1\n"
                      " LIMIT :param_1 OFFSET :param_2")

    assert actual_query == expected_query


@pytest.mark.asyncio
async def test_build_update_query(empty_user_storage: UserStorage):
    actual_query = str(empty_user_storage._build_update_query(
        (User.is_verified == False) & (User.telegram_id == 32),  # type: ignore
        is_verified=True,
    ))

    expected_query = ('UPDATE users SET is_verified=:is_verified WHERE users.is_verified = false '
                      'AND users.telegram_id = :telegram_id_1')

    assert actual_query == expected_query


@pytest.mark.asyncio
async def test_build_delete_query(empty_user_storage: UserStorage):
    actual_query = str(empty_user_storage._build_delete_query(User.telegram_id == 1))

    expected_query = "DELETE FROM users WHERE users.telegram_id = :telegram_id_1"

    assert actual_query == expected_query
