import asyncio

from boosty import BoostyProfileStorage

from user.domain.models import BoostyProfile, Channel, User
from user.service_layer.unit_of_work import UnitOfWork


async def list_channels(
    user_id: int,
    channels: list[dict],
    storage: BoostyProfileStorage,
    uow: UnitOfWork,
) -> set[Channel]:
    async with uow:
        user: User | None = await uow.user_storage.get(user_id)
        tasks = [storage.get_by_email(email.email) for email in user.emails if email.is_verified]

        profiles: tuple[BoostyProfile] = await asyncio.gather(*tasks)

        accessible_channels = set[Channel]()

        for channel in channels:
            for profile in profiles:
                if profile.level.id == channel["level_id"]:
                    accessible_channels.add(
                        Channel(
                            id=channel["id"],
                            invite_link=channel["invite_link"],
                            level=profile.level,
                        )
                    )

        return accessible_channels
