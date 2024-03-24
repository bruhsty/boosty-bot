from typing import Iterable

import sqlalchemy as sa
from common.adapters.storage import AbstractStorage
from common.domain import DomainEvent
from registration.domain import models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from . import schema


class UserStorage(AbstractStorage):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.seen = set[models.User]()

    async def add(self, user: models.User) -> None:
        self.session.add(schema.User.from_model(user))
        self.seen.add(user)

    async def get(self, user_id: int) -> models.User | None:
        load_profiles = joinedload(schema.User.boosty_profiles)
        load_profile_level = load_profiles.joinedload(schema.BoostyProfile.level)
        load_verification_codes = load_profiles.joinedload(schema.BoostyProfile.verification_codes)

        query = (
            sa.select(schema.User)
            .where(schema.User.telegram_id == user_id)
            .options(load_profiles, load_profile_level, load_verification_codes)
        )

        result = (await self.session.execute(query)).unique().one_or_none()

        if result is None:
            return None

        user = result[0].to_model()
        self.seen.add(user)

        return user

    async def collect_events(self) -> Iterable[DomainEvent]:
        new_events = []
        for user in self.seen:
            new_events.extend(user.pop_all_events())
        return new_events

    async def close(self) -> None:
        self.seen.clear()
