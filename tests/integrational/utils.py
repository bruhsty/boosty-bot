import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ["insert_user"]


async def insert_user(session: AsyncSession) -> None:
    await session.execute(sa.text("INSERT INTO users (telegram_id) VALUES (12345678)"))

    await session.execute(
        sa.text(
            "INSERT INTO boosty_subscription_levels (name, price, is_archived) "
            "VALUES ('sub level name', 200, false)"
        )
    )

    await session.execute(
        sa.text(
            "INSERT INTO boosty_profiles"
            "(profile_id, user_id, name, email, level_id, next_pay_time, banned)"
            "VALUES (123, 12345678, 'John Doe', 'johndoe@example.com', 1, now(), false)"
        )
    )
