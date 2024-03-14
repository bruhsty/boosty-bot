import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from bruhsty.storage.sql.base import Base
from .. import models


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(sa.Integer(), primary_key=True)
    email: Mapped[str] = mapped_column(sa.String(128), index=True)
    is_verified: Mapped[bool] = mapped_column(sa.Boolean())

    def to_model(self) -> models.User:
        return models.User(
            telegram_id=self.telegram_id,
            email=self.email,
            is_verified=self.is_verified,
        )
