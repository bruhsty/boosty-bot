import dataclasses
import json
from datetime import timedelta

from redis import asyncio
from user.domain.models import BoostyProfile


def profile_key(email: str) -> str:
    return f"boosty:profile:{email}"


def dump_profile(profile: BoostyProfile) -> str:
    data = dataclasses.asdict(profile)
    return json.dumps(data)


def load_profile(data: str) -> BoostyProfile:
    return BoostyProfile(**json.loads(data))


class BoostyProfileStorage:
    def __init__(
        self,
        redis: asyncio.Redis,
        level_lifetime: timedelta,
    ) -> None:
        self.redis = redis
        self.level_lifetime = level_lifetime

    async def add(self, *profiles: BoostyProfile) -> None:
        with self.redis.pipeline(transaction=False) as pipe:
            for profile in profiles:
                content = dump_profile(profile)
                await pipe.set(profile_key(profile.email), content)

    async def get_by_email(self, email: str) -> BoostyProfile:
        content = await self.redis.get(email)
        return load_profile(content)
