from __future__ import annotations

import dataclasses
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from . import events
from .abc import Aggregate
from .errors import ProfileNotLinked


@dataclass
class BoostyProfile:
    id: int
    email: str
    name: str
    level: SubscriptionLevel | None
    next_pay_time: datetime | None
    banned: bool
    verification_codes: list[VerificationCode]

    @property
    def is_verified(self) -> bool:
        return any(code.used_at is not None for code in self.verification_codes)

    @property
    def subscribed(self):
        return self.level is not None

    def __eq__(self, other: BoostyProfile) -> bool:
        if type(other) is not BoostyProfile:
            return False

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class SubscriptionLevel:
    id: int
    name: str
    price: int
    is_archived: bool

    def __eq__(self, other: SubscriptionLevel) -> bool:
        if type(other) is not SubscriptionLevel:
            return False

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class VerificationCode:
    id: uuid.UUID
    value: str
    valid_until: datetime
    replaced_with: uuid.UUID | None
    used_at: datetime | None
    created_at: datetime = datetime.now()

    def __eq__(self, other: VerificationCode) -> bool:
        if type(other) is not VerificationCode:
            return False

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class User(Aggregate[int]):
    def __init__(self, telegram_id: int, profiles: Sequence[BoostyProfile]) -> None:
        super().__init__(telegram_id)
        self.telegram_id = telegram_id
        self._profiles = set[BoostyProfile](profiles)

    @classmethod
    def new(cls, telegram_id: int) -> User:
        return cls(telegram_id, [])

    def add_profile(self, profile: BoostyProfile) -> BoostyProfile:
        if profile in self._profiles:
            return profile

        self._profiles.add(dataclasses.replace(profile))

        event = events.BoostyProfileAdded(
            time=datetime.now(),
            user_id=self.id,
            profile_id=profile.id,
            profile_email=profile.email,
            profile_name=profile.name,
        )
        self._push_event(event)
        return profile

    def verify_profile(self, profile: BoostyProfile, code_value: str) -> None:
        if profile not in self._profiles:
            raise ProfileNotLinked(
                f"Profile {profile.email} ({profile.name}) is not linked to user {self.telegram_id}"
            )

        now = datetime.now()

        def code_is_valid(c: VerificationCode) -> bool:
            code_not_used = c.used_at is None
            code_not_expired = now <= c.valid_until
            code_not_replaced = c.replaced_with is None
            same_value = c.value == code_value
            return same_value and code_not_used and code_not_expired and code_not_replaced

        try:
            code = next(c for c in profile.verification_codes if code_is_valid(c))
            code.used_at = now
            event = events.BoostyProfileVerified(
                time=now,
                user_id=self.id,
                profile_id=profile.id,
                profile_email=profile.email,
                profile_name=profile.name,
            )
            self._push_event(event)
        except StopIteration:
            return None

    @property
    def profiles(self) -> set[BoostyProfile]:
        return set(self._profiles)

    def __eq__(self, other: User) -> bool:
        if type(other) is not User:
            return False

        return self.telegram_id == other.telegram_id

    def __hash__(self) -> int:
        return hash(self.telegram_id)
