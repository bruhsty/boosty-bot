from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import functions
from bruhsty.storage.sql.base import Base

__all__ = ["VerificationCode"]

from bruhsty.storage.verification_codes import Code


class VerificationCode(Base):
    __tablename__ = "verification_codes"
    code_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column()
    email: Mapped[str] = mapped_column(String(64))
    code: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=functions.now())
    valid_until: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[bool | None] = mapped_column(default=None, nullable=True)

    def to_model(self) -> Code:
        return Code(
            code_id=self.code_id,
            code=self.code,
            email=self.email,
            telegram_id=self.telegram_id,
            used_at=self.used_at,
            created_at=self.created_at,
            valid_until=self.valid_until,
        )
