from __future__ import annotations

import uuid
from datetime import datetime

import sqlalchemy as sa
from common.orm import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

from user.domain import models

__all__ = ["User", "UserEmail", "VerificationCode"]


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
        cascade="save-update, merge, delete, delete-orphan",
        lazy="noload",
    )

    def to_model(self) -> models.User:
        return models.User.make(
            telegram_id=self.telegram_id,
            emails=[email.to_model() for email in self.emails],
        )

    @classmethod
    def from_model(cls, model: models.User) -> User:
        return User(
            telegram_id=model.id,
            emails=[UserEmail.from_model(email, model.id) for email in model.emails],
        )


class VerificationCode(Base, CreatedAtMixin):
    __tablename__ = "verification_codes"

    code_id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True)
    value: Mapped[str] = mapped_column(sa.String(length=10), index=True)
    valid_until: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True))
    assigned_to_user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.telegram_id"))
    email: Mapped[str] = mapped_column(sa.ForeignKey("user_emails.email"))
    used_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), default=None, nullable=True
    )
    replaced_with_code_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("verification_codes.code_id"), default=None, nullable=True
    )
    replaced_with: Mapped[VerificationCode] = relationship(
        "VerificationCode",
        lazy="noload",
        cascade="all, delete-orphan",
        remote_side=[code_id],
        single_parent=True,
    )

    def to_model(self) -> models.VerificationCode:
        return models.VerificationCode(
            id=self.code_id,
            value=self.value,
            valid_until=self.valid_until,
            replaced_with=None,
            replaced_with_id=self.replaced_with_code_id,
            used_at=self.used_at,
            created_at=self.created_at,
        )

    @classmethod
    def from_model(
        cls, model: models.VerificationCode, assigned_to_user_id: int
    ) -> VerificationCode:
        if model.replaced_with:
            replaced_with = VerificationCode.from_model(model.replaced_with, assigned_to_user_id)
        else:
            replaced_with = None

        return cls(
            assigned_to_user_id=assigned_to_user_id,
            code_id=model.id,
            value=model.value,
            valid_until=model.valid_until,
            used_at=model.used_at,
            replaced_with=replaced_with,
            replaced_with_code_id=model.replaced_with_id,
        )


class UserEmail(Base, CreatedAtMixin):
    __tablename__ = "user_emails"

    email: Mapped[str] = mapped_column(sa.String(), primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.telegram_id"))
    verification_codes: Mapped[list[str]] = relationship(
        VerificationCode,
        cascade="all, delete-orphan",
        lazy="noload",
    )

    def to_model(self) -> models.Email:
        return models.Email(
            email=self.email,
            verification_codes=[c.to_model() for c in self.verification_codes],
        )

    @classmethod
    def from_model(cls, model: models.Email, user_id: int) -> UserEmail:
        return cls(
            email=model.email,
            verification_codes=[
                VerificationCode.from_model(c, user_id) for c in model.verification_codes
            ],
        )
