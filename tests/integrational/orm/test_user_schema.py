import datetime

import pytest
import sqlalchemy as sa
from registration.adapters.storage.schema import SubscriptionLevel, User
from registration.domain import models
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def execute_text(session: AsyncSession, query: str) -> tuple:
    return tuple((await session.execute(sa.text(query))).all())


@pytest.mark.asyncio
async def test_user_schema_can_save_user(session: AsyncSession):
    profile = BoostyProfile(
        name="John Doe",
        email="johndoe@example.com",
        next_pay_time=datetime.datetime(2077, 1, 1),
        level=SubscriptionLevel(
            name="Paid subscription level",
            price=200,
        ),
        banned=False,
    )
    user = User(
        telegram_id=123,
        boosty_profiles=[
            profile,
        ],
    )
    session.add(user)
    await session.commit()

    [[telegram_id]] = await execute_text(
        session,
        "SELECT telegram_id FROM users WHERE telegram_id=123",
    )

    assert telegram_id == 123

    [[level_id, name, email]] = await execute_text(
        session,
        "SELECT level_id, name, email FROM boosty_profiles WHERE user_id=123",
    )

    assert name == "John Doe"
    assert email == "johndoe@example.com"

    [[name, price]] = await execute_text(
        session,
        f"SELECT name, price FROM boosty_subscription_levels WHERE level_id={level_id}",
    )

    assert name == "Paid subscription level"
    assert price == 200


@pytest.mark.asyncio
async def test_user_schema_raises_if_telegram_id_duplicated(session: AsyncSession):
    user = User(
        telegram_id=123,
        boosty_profiles=[],
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
        boosty_profiles=[
            BoostyProfile(
                name="John Doe",
                email="johndoe@example.com",
                next_pay_time=datetime.datetime(2077, 1, 1),
                level=SubscriptionLevel(
                    name="Paid subscription level",
                    price=200,
                ),
                banned=False,
            ),
        ],
    )

    session.add(user)
    await session.commit()

    user.boosty_profiles[0].name = "John Smith"
    session.add(user)
    await session.commit()

    [[name]] = await execute_text(session, "SELECT name FROM boosty_profiles WHERE user_id=123")

    assert name == "John Smith"


@pytest.mark.asyncio
async def test_can_append_boosty_profile_to_user(session: AsyncSession):
    profile = BoostyProfile(
        name="John Doe",
        email="johndoe@example.com",
        next_pay_time=datetime.datetime(2077, 1, 1),
        level=SubscriptionLevel(
            name="Paid subscription level",
            price=200,
        ),
        banned=False,
    )

    user = User(telegram_id=123, boosty_profiles=[])
    session.add(user)
    await session.commit()

    user.boosty_profiles.append(profile)
    session.add(user)
    await session.commit()

    [[exists]] = await execute_text(
        session, "SELECT true FROM boosty_profiles WHERE name='John Doe'"
    )
    assert exists


@pytest.mark.asyncio
async def test_profile_is_deleted_if_removed_from_user(session: AsyncSession):
    user = User(
        telegram_id=123,
        boosty_profiles=[
            BoostyProfile(
                name="John Doe",
                email="johndoe@example.com",
                next_pay_time=datetime.datetime(2077, 1, 1),
                level=SubscriptionLevel(
                    name="Paid subscription level",
                    price=200,
                ),
                banned=False,
            ),
        ],
    )

    session.add(user)
    await session.commit()
    user.boosty_profiles.pop()
    await session.commit()

    [[count]] = await execute_text(session, "SELECT count(*) FROM boosty_profiles")
    assert count == 0


@pytest.mark.asyncio
async def test_user_to_model_when_user_saved(session: AsyncSession):
    user = User(
        telegram_id=123,
        boosty_profiles=[
            BoostyProfile(
                name="John Doe",
                email="johndoe@example.com",
                next_pay_time=datetime.datetime(2077, 1, 1),
                level=SubscriptionLevel(
                    name="Paid subscription level",
                    price=200,
                    is_archived=True,
                ),
                banned=False,
            ),
        ],
    )
    session.add(user)
    await session.commit()
    model = user.to_model()
    assert type(model) is models.User
    assert model.id == 123
    assert len(model.profiles) == 1
    profile = model.profiles.pop()
    assert profile.id == 1
    assert profile.name == "John Doe"
    assert profile.email == "johndoe@example.com"
    assert profile.next_pay_time == datetime.datetime(2077, 1, 1)
    assert profile.level.name == "Paid subscription level"
    assert profile.level.price == 200
    assert profile.level.is_archived is True
