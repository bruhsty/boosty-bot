import datetime
import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from user.adapters.storage.schema import User, UserEmail, VerificationCode


async def execute_text(session: AsyncSession, query: str) -> tuple:
    return tuple((await session.execute(sa.text(query))).all())


@pytest.mark.asyncio
async def test_user_schema_can_save_user(session: AsyncSession):
    expected_valid_until = datetime.datetime(2077, 1, 1, tzinfo=datetime.timezone.utc)
    expected_code_id = uuid.uuid4()
    user = User(
        telegram_id=123,
        emails=[
            UserEmail(
                email="johndoe@example.com",
                verification_codes=[
                    VerificationCode(
                        code_id=expected_code_id,
                        email="johndoe@example.com",
                        valid_until=expected_valid_until,
                        value="123-456",
                        assigned_to_user_id=123,
                    )
                ],
            )
        ],
    )
    session.add(user)
    await session.commit()

    [[telegram_id]] = await execute_text(
        session,
        "SELECT telegram_id FROM users WHERE telegram_id=123",
    )

    assert telegram_id == 123

    [[email]] = await execute_text(
        session,
        "SELECT email FROM user_emails WHERE user_id=123",
    )

    assert email == "johndoe@example.com"

    [[code_id, value, valid_until]] = await execute_text(
        session,
        "SELECT code_id, value, valid_until FROM verification_codes "
        "WHERE email='johndoe@example.com' AND assigned_to_user_id=123",
    )
    assert code_id == expected_code_id
    assert value == "123-456"
    assert valid_until == expected_valid_until


@pytest.mark.asyncio
async def test_user_schema_raises_if_telegram_id_duplicated(session: AsyncSession):
    user = User(
        telegram_id=123,
    )
    session.add(user)

    await session.commit()

    user2 = User(
        telegram_id=123,
    )

    session.add(user2)

    with pytest.raises(IntegrityError):
        await session.commit()


@pytest.mark.asyncio
async def test_user_schema_watches_profile_updates(session: AsyncSession):
    user = User(
        telegram_id=123,
        emails=[
            UserEmail(email="johndoe@example.com"),
        ],
    )

    session.add(user)
    await session.commit()

    user.emails.append(
        UserEmail(
            email="johndoe1@example.com",
        )
    )
    session.add(user)
    await session.commit()

    [[email], [email1]] = await execute_text(
        session, "SELECT email FROM user_emails WHERE user_id=123 ORDER BY email"
    )

    assert email == "johndoe1@example.com"
    assert email1 == "johndoe@example.com"


@pytest.mark.asyncio
async def test_profile_is_deleted_if_removed_from_user(session: AsyncSession):
    user = User(
        telegram_id=123,
        emails=[
            UserEmail(email="johndoe@example.com"),
        ],
    )

    session.add(user)
    await session.commit()
    user.emails.pop()
    await session.commit()

    [[count]] = await execute_text(session, "SELECT count(*) FROM user_emails")
    assert count == 0
