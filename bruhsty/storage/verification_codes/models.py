from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict

__all__ = ["Code", "EditableFields"]

from bruhsty.storage.specs import Field


@dataclass
class Code:
    code_id: int
    telegram_id: int
    email: str
    code: str
    created_at: datetime
    used_at: datetime | None
    valid_until: datetime

    class Fields:
        code_id = Field("code_id")
        telegram_id = Field("telegram_id")
        email = Field("email")
        code = Field("code")
        created_at = Field("created_at")
        used_at = Field("used_at")
        valid_until = Field("valid_until")


class EditableFields(TypedDict):
    telegram_id: int
    email: str
    code: str
    created_at: datetime
    used_at: datetime | None
    valid_until: datetime
