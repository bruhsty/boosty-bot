import typing
from datetime import timedelta, datetime
from typing import Any, override, AsyncIterable, Sequence

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from . import schema

from .. import Code, CodeEdit, CodeCreate
from ...specs import Specification

from ...sql import BaseSQLStorage

__all__ = ["CodeStorage"]


class CodeStorage(BaseSQLStorage):
    Schema = schema.Code
    ModelCreate = CodeCreate
    ModelGet = Code
    ModelUpdate = CodeEdit

    def __init__(
            self,
            session_maker: async_sessionmaker[AsyncSession],
            code_ttl: timedelta,
    ) -> None:
        super().__init__(session_maker)
        self.code_ttl = code_ttl

    if typing.TYPE_CHECKING:
        async def create(self, model: CodeCreate) -> Code:
            ...

        async def find(
                self,
                filter_: Specification,
                limit: int | None = None,
                offset: int | None = None,
        ) -> AsyncIterable[Code]:
            ...

        async def find_all(
                self,
                filter_: Specification,
                limit: int | None = None,
                offset: int | None = None,
        ) -> Sequence[Code]:
            ...

        async def update(
                self,
                filter_: Specification,
                **updates: CodeEdit,
        ) -> None:
            ...

    @override
    def resolve_name(self, name: str) -> Any:
        return {
            "code_id": schema.VerificationCode.code_id,
            "code": schema.VerificationCode.code,
            "telegram_id": schema.VerificationCode.telegram_id,
            "email": schema.VerificationCode.email,
            "used_at": schema.VerificationCode.used_at,
            "valid_until": schema.VerificationCode.valid_until,
            "created_at": schema.VerificationCode.created_at,
        }[name]

    @override
    def model_to_schema(self, model: CodeCreate) -> schema.VerificationCode:
        now = datetime.now()
        default_valid_until = now + self.code_ttl
        return schema.VerificationCode(
            telegram_id=model.telegram_id,
            email=model.email,
            code=model.code,
            used_at=None,
            valid_until=model.valid_until or default_valid_until,
            created_at=now,
        )

    @override
    def schema_to_model(self, schema: Any) -> Any:
        pass

    async def close(self) -> None:
        pass
