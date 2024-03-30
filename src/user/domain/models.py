from __future__ import annotations

import functools
import os
import struct
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Sequence

from common.domain import Aggregate, DomainError

from .events import EmailVerified, VerificationCodeIssued


class EmailNotLinkedError(DomainError):
    pass


class InvalidCodeError(DomainError):
    pass


@dataclass
class BoostyProfile:
    id: int
    email: str
    name: str
    level: SubscriptionLevel | None
    next_pay_time: datetime | None
    banned: bool

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
    replaced_with: VerificationCode | None
    replaced_with_id: uuid.UUID | None
    used_at: datetime | None
    created_at: datetime = field(
        default_factory=functools.partial(datetime.now, tzinfo=timezone.utc)
    )

    @property
    def replaced(self) -> bool:
        return self.replaced_with_id is not None

    def replace(self, code: VerificationCode) -> None:
        if self.replaced:
            raise DomainError(
                f"Verification code {self.id} has already been "
                f"replaced with {self.replaced_with_id}"
            )

        self.replaced_with = code
        self.replaced_with_id = code.id

    def __eq__(self, other: VerificationCode) -> bool:
        if type(other) is not VerificationCode:
            return False

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class Email:
    email: str
    verification_codes: list[VerificationCode]

    @property
    def is_verified(self) -> bool:
        return any(code.used_at is not None for code in self.verification_codes)

    @property
    def active_verification_code(self) -> VerificationCode | None:
        now = datetime.now(timezone.utc)

        def code_is_valid(c: VerificationCode) -> bool:
            code_not_used = c.used_at is None
            code_not_expired = now <= c.valid_until
            return code_not_used and code_not_expired and not c.replaced

        try:
            return next(c for c in self.verification_codes if code_is_valid(c))
        except StopIteration:
            return None


def generate_random_code() -> str:
    raw_bytes = os.urandom(4)
    value = struct.unpack("!i", raw_bytes)[0] % 10000
    return str(value)


class User(Aggregate[int]):
    CODE_TTL = timedelta(minutes=30)
    CODE_GENERATOR = staticmethod(generate_random_code)

    def __init__(
        self,
        telegram_id: int,
    ) -> None:
        super().__init__(telegram_id)
        self.telegram_id = telegram_id
        self._emails = list[Email]()

    @classmethod
    def make(cls, telegram_id: int, emails: Sequence[Email]) -> User:
        user = cls(telegram_id)
        user._emails = list(emails)
        return user

    def add_email(self, new_email: str) -> None:
        if self._get_email(new_email) is not None:
            return

        self._emails.append(Email(new_email, []))
        self.issue_verification_code(new_email, self.CODE_GENERATOR())

    def remove_email(self, email: str) -> None:
        self._emails = [e for e in self._emails if e.email != email]

    def verify_email(self, unverified_email: str, code_value: str) -> None:
        email = self._get_email(unverified_email)
        if email is None:
            raise EmailNotLinkedError(f"Email {unverified_email} is not linked to user {self.id}")

        now = datetime.now(tz=timezone.utc)

        code = email.active_verification_code
        if code is None or code.value != code_value:
            raise InvalidCodeError("Provided verification code is invalid")

        code.used_at = now
        event = EmailVerified(
            time=now,
            user_id=self.id,
            email=unverified_email,
            code_id=code.id,
        )
        self._push_event(event)

    def issue_verification_code(self, unverified_email: str, code_value: str) -> None:
        email = self._get_email(unverified_email)
        if email is None:
            raise EmailNotLinkedError(f"Email {unverified_email} is not linked to user {self.id}")

        now = datetime.now(tz=timezone.utc)
        new_code = VerificationCode(
            id=uuid.uuid4(),
            value=code_value,
            used_at=None,
            valid_until=now + self.CODE_TTL,
            replaced_with=None,
            replaced_with_id=None,
            created_at=now,
        )

        unused_code = email.active_verification_code
        if unused_code is not None:
            unused_code.replace(new_code)

        email.verification_codes.insert(0, new_code)
        self._push_event(
            VerificationCodeIssued(
                time=now,
                user_id=self.id,
                email=unverified_email,
                code_id=new_code.id,
                code=code_value,
                code_valid_until=new_code.valid_until,
            )
        )

    @property
    def emails(self) -> tuple[Email, ...]:
        return tuple(self._emails)

    @property
    def has_email(self) -> bool:
        return len(self._emails) > 0

    def _get_email(self, email: str) -> Email | None:
        try:
            return next(e for e in self._emails if e.email == email)
        except StopIteration:
            return None

    def __eq__(self, other: User) -> bool:
        if type(other) is not User:
            return False

        return self.telegram_id == other.telegram_id

    def __hash__(self) -> int:
        return hash(self.telegram_id)
