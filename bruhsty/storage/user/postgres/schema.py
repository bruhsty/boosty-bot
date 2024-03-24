from __future__ import annotations

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bruhsty.domain import models
from bruhsty.storage.sql.base import Base


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        default=sa.func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
        onupdate=sa.func.now(),
        default=None,
        server_default=None,
    )


class User(Base, CreatedAtMixin):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(sa.Integer(), primary_key=True)
    boosty_profiles: Mapped[list[BoostyProfile]] = relationship(
        cascade="all, delete-orphan",
        lazy="noload",
    )

    def to_model(self) -> models.User:
        return models.User(
            telegram_id=self.telegram_id,
            profiles=[p.to_model() for p in self.boosty_profiles],
        )

    @classmethod
    def from_model(cls, model: models.User) -> User:
        return User(
            telegram_id=model.id,
            boosty_profiles=[BoostyProfile.from_model(p) for p in model.profiles],
        )


class BoostyProfile(Base, CreatedAtMixin):
    __tablename__ = "boosty_profiles"

    profile_id: Mapped[int] = mapped_column(sa.Integer(), primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.telegram_id"))
    name: Mapped[str]
    email: Mapped[str]
    level_id: Mapped[int] = mapped_column(
        sa.ForeignKey("boosty_subscription_levels.level_id"), nullable=True
    )
    level: Mapped[SubscriptionLevel] = relationship(
        cascade="all, delete-orphan",
        single_parent=True,
        lazy="noload",
    )
    next_pay_time: Mapped[datetime]
    banned: Mapped[bool]
    verification_codes: Mapped[list[VerificationCode]] = relationship(
        cascade="all, delete-orphan", lazy="noload"
    )

    def to_model(self) -> models.BoostyProfile:
        return models.BoostyProfile(
            id=self.profile_id,
            email=self.email,
            name=self.name,
            level=self.level.to_model() if self.level else None,
            next_pay_time=self.next_pay_time,
            banned=self.banned,
            verification_codes=[c.to_model() for c in self.verification_codes],
        )

    @classmethod
    def from_model(cls, model: models.BoostyProfile) -> BoostyProfile:
        return BoostyProfile(
            profile_id=model.id,
            name=model.name,
            email=model.email,
            level=SubscriptionLevel.from_model(model.level) if model.level else None,
            next_pay_time=model.next_pay_time,
            banned=model.banned,
        )


class SubscriptionLevel(Base, CreatedAtMixin):
    __tablename__ = "boosty_subscription_levels"

    level_id: Mapped[int] = mapped_column(sa.Integer(), primary_key=True, autoincrement=True)
    name: Mapped[str]
    price: Mapped[int]
    is_archived: Mapped[bool] = mapped_column(sa.Boolean(), default=False)

    def to_model(self) -> models.SubscriptionLevel:
        return models.SubscriptionLevel(
            id=self.level_id,
            name=self.name,
            price=self.price,
            is_archived=self.is_archived,
        )

    @classmethod
    def from_model(cls, model: models.SubscriptionLevel) -> SubscriptionLevel:
        return SubscriptionLevel(
            level_id=model.id,
            name=model.name,
            price=model.price,
            is_archived=model.is_archived,
        )


class VerificationCode(Base, CreatedAtMixin):
    __tablename__ = "verification_codes"

    code_id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    value: Mapped[str]
    valid_until: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True))
    assigned_to_user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.telegram_id"))
    assigned_to_profile_id: Mapped[int] = mapped_column(sa.ForeignKey("boosty_profiles.profile_id"))
    used_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), default=None, nullable=True
    )
    replaced_with_code_id: Mapped[int] = mapped_column(
        sa.ForeignKey("verification_codes.code_id"), default=None, nullable=True
    )

    def to_model(self) -> models.VerificationCode:
        return models.VerificationCode()
