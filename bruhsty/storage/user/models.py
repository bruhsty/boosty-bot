from typing import TypedDict

from bruhsty.storage.specs import Field


class User:
    telegram_id = Field[int]()
    email = Field[str]()
    is_verified = Field[bool]()

    def __init__(
        self,
        telegram_id: int,
        email: str,
        is_verified: bool,
    ) -> None:
        self.telegram_id = telegram_id
        self.email = email
        self.is_verified = is_verified


class UserUpdate(TypedDict):
    email: str
    is_verified: bool
