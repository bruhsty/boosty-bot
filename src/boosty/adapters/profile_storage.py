import dataclasses
import json
from datetime import datetime, timedelta
from typing import Any

from redis import asyncio
from user.domain.models import BoostyProfile, SubscriptionLevel


def profile_key(email: str) -> str:
    return f"boosty:profile:{email}"


def dump_profile(profile: BoostyProfile) -> str:
    def serializer(value: Any) -> Any:
        mapper = {
            datetime: datetime.isoformat,
        }
        return mapper.get(type(value), str)(value)

    data = dataclasses.asdict(profile)
    return json.dumps(data, default=serializer)


def load_profile(data: str) -> BoostyProfile:
    json_data = json.loads(data)
    json_data["level"] = SubscriptionLevel(**json_data["level"])
    profile = BoostyProfile(**json_data)
    return profile


class BoostyProfileStorage:
    def __init__(
        self,
        redis: asyncio.Redis,
        level_lifetime: timedelta,
    ) -> None:
        self.redis = redis
        self.level_lifetime = level_lifetime

    async def add(self, *profiles: BoostyProfile) -> None:
        async with self.redis.pipeline(transaction=True) as pipe:
            for profile in profiles:
                content = dump_profile(profile)
                pipe = pipe.set(profile_key(profile.email), content)
            await pipe.execute()

    async def get_by_email(self, email: str) -> BoostyProfile | None:
        content = await self.redis.get(profile_key(email))
        return load_profile(content) if content is not None else None
