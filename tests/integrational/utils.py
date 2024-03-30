from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ["insert_user"]


async def insert_user(session: AsyncSession) -> None:
    await session.execute(sa.text("INSERT INTO users (telegram_id) VALUES (12345678)"))

    await session.execute(
        sa.text(
            "INSERT INTO user_emails (email, user_id) " "VALUES ('johndoe@example.com', 12345678)"
        )
    )

    valid_until = datetime(2077, 1, 1, tzinfo=timezone.utc)

    await session.execute(
        sa.text(
            "INSERT INTO verification_codes "
            "(code_id, value, valid_until, "
            "assigned_to_user_id, used_at, replaced_with_code_id, email) "
            "VALUES "
            "("
            "   '536462d6-6b82-46b8-ab34-20f415d9af16', '123-456', "
            "   :valid_until, 12345678, NULL, NULL, 'johndoe@example.com'"
            ")",
        ),
        {"valid_until": valid_until},
    )
