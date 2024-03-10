from datetime import datetime
from typing import TypedDict

__all__ = ["Code", "EditableFields"]

from bruhsty.storage.specs import Field


class Code:
    code_id = Field[int]()
    telegram_id = Field[int]()
    email = Field[str]()
    code = Field[str]()
    created_at = Field[datetime]()
    used_at = Field[datetime | None]()
    valid_until = Field[datetime]()

    def __init__(
            self,
            code_id: int,
            telegram_id: int,
            email: str,
            code: str,
            created_at: datetime,
            valid_until: datetime,
            used_at: datetime | None = None,
    ) -> None:
        self.code_id = code_id
        self.telegram_id = telegram_id
        self.email = email
        self.code = code
        self.created_at = created_at
        self.valid_until = valid_until
        self.used_at = used_at


class EditableFields(TypedDict):
    telegram_id: int
    email: str
    code: str
    created_at: datetime
    used_at: datetime | None
    valid_until: datetime
