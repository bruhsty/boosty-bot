from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bruhsty.storage.sql.base import Base
from bruhsty.domain import models


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=sa.func.now())


class User(Base, CreatedAtMixin):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(sa.Integer(), primary_key=True)
    boosty_profiles: Mapped[list[BoostyProfile]] = relationship(
        cascade="all, delete-orphan"
    )
    is_verified: Mapped[bool] = False
    verification_codes: Mapped[list[VerificationCode]] = relationship(
        cascade="all, delete-orphan"
    )

    def to_model(self) -> models.User:
        return models.User(
            telegram_id=self.telegram_id,
            profiles=[p.to_model() for p in self.boosty_profiles],
        )

    @classmethod
    def from_model(cls, model: models.User) -> User:
        raise NotImplementedError


class BoostyProfile(Base, CreatedAtMixin):
    __tablename__ = "boosty_profiles"

    profile_id: Mapped[int] = mapped_column(sa.Integer(), primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.telegram_id"))
    name: Mapped[str]
    email: Mapped[str]
    level_id: Mapped[int] = mapped_column(sa.ForeignKey("boosty_subscription_levels.level_id"), nullable=True)
    level: Mapped[SubscriptionLevel] = relationship()
    next_pay_time: Mapped[datetime]
    banned: Mapped[bool]

    def to_model(self) -> models.BoostyProfile:
        return models.BoostyProfile(
            id=self.profile_id,
            email=self.email,
            name=self.name,
            level=self.level.to_model() if self.level else None,
            next_pay_time=self.next_pay_time,
            subscribed=self.level is not None,
            banned=self.banned,
        )

    @classmethod
    def from_model(cls, model: models.BoostyProfile) -> User:
        raise NotImplementedError


class SubscriptionLevel(Base, CreatedAtMixin):
    __tablename__ = "boosty_subscription_levels"

    level_id: Mapped[int] = mapped_column(sa.Integer(), primary_key=True, autoincrement=True)
    name: Mapped[str]
    price: Mapped[int]


class VerificationCode(Base, CreatedAtMixin):
    __tablename__ = "verification_codes"

    code_id: Mapped[int] = mapped_column(sa.Integer(), primary_key=True, autoincrement=True)
    value: Mapped[str]
    valid_until: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True))
    assigned_to_user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.telegram_id"))
    assigned_to_profile_id: Mapped[int] = mapped_column(sa.ForeignKey("boosty_profiles.profile_id"))
    used_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=None, nullable=True)
    is_valid: Mapped[bool] = False
