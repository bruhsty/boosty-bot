from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict

__all__ = ["Code", "EditableFields"]


@dataclass
class Code:
    code_id: int
    telegram_id: int
    email: str
    code: str
    created_at: datetime
    used_at: datetime | None
    valid_until: datetime


class EditableFields(TypedDict):
    telegram_id: int
    email: str
    code: str
    created_at: datetime
    used_at: datetime | None
    valid_until: datetime
