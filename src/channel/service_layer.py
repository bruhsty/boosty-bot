import asyncio

from boosty import BoostyProfileStorage
from user.domain.models import User

from config import Channel


async def can_access_channel(
    user: User | None,
    storage: BoostyProfileStorage,
    channel: Channel,
) -> bool:
    if user is None:
        return False

    profiles = await asyncio.gather(
        *[storage.get_by_email(email.email) for email in user.emails if email.is_verified]
    )

    return any(p.level.id == channel["level_id"] for p in profiles)
