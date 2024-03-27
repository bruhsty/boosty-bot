from __future__ import annotations

import uuid
from datetime import datetime

import sqlalchemy as sa
from common.orm import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

from registration.domain import models

__all__ = ["User", "SubscriptionLevel", "VerificationCode"]


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

    emails: Mapped[list[UserEmail]] = relationship(
        cascade="all, delete-orphan",
        lazy="noload",
    )

    def to_model(self) -> models.User:
        return models.User(
            telegram_id=self.telegram_id,
            emails=[email.to_model() for email in self.emails],
        )

    @classmethod
    def from_model(cls, model: models.User) -> User:
        return User(
            telegram_id=model.id, emails=[UserEmail.from_orm(email) for email in model.emails]
        )


class UserEmail(Base, CreatedAtMixin):
    __tablename__ = "user_emails"

    email: Mapped[str] = mapped_column(sa.String(), primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.telegram_id"))

    def to_model(self) -> models.Email:
        pass

    def from_model(cls, model: models.Email) -> UserEmail:
        pass


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
    value: Mapped[str] = mapped_column(sa.String(length=10), index=True)
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
