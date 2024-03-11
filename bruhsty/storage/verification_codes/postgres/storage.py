import functools
import operator
from datetime import datetime, timedelta
from typing import Any, AsyncIterable

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from typing_extensions import Unpack

from . import schema
import sqlalchemy as sa

__all__ = ["CodeStorage"]

from ..errors import CodeNotFoundError
from ..models import Code, EditableFields
from ...specs import Specification, Compare, Or, And, Not, Operator


class CodeStorage:

    def __init__(
            self,
            session_maker: async_sessionmaker[AsyncSession],
            code_ttl: timedelta,
    ) -> None:
        self.session_maker = session_maker
        self.code_ttl = code_ttl

    async def add(self, telegram_id: int, email: str, code: str) -> Code:
        async with self.session_maker() as session:
            now = datetime.now()
            valid_until = now + self.code_ttl
            code_obj = schema.VerificationCode(
                telegram_id=telegram_id,
                email=email,
                code=code,
                created_at=now,
                valid_until=valid_until,
                used_at=None,
            )
            session.add(code_obj)
            await session.commit()

        return code_obj.to_model()

    async def delete(self, code_id: int) -> None:
        async with self.session_maker() as session:
            query = sa.delete(schema.VerificationCode).where(schema.VerificationCode.code_id == code_id)
            result = await session.execute(query)
            if result.supports_sane_rowcount() and result.rowcount() == 0:
                raise CodeNotFoundError(code_id, "Unable to delete code that does not exist")

            await session.commit()

    async def update(self, code_id: int, **updates: Unpack[EditableFields]) -> None:
        async with self.session_maker() as session:
            await session.execute(
                sa
                .update(schema.VerificationCode)
                .where(schema.VerificationCode.code_id == code_id)
                .values(**updates)
            )

    async def find(self, spec: Specification) -> AsyncIterable[Code]:
        where_clause = _spec_to_query(spec)
        async with self.session_maker() as session:
            selected_codes = await session.stream_scalars(
                sa.
                select(schema.VerificationCode).
                where(where_clause)
            )
            async for code in selected_codes:
                code: schema.VerificationCode
                yield code.to_model()

    async def close(self) -> None:
        pass


def _spec_to_query(spec: Specification) -> Any:
    mapper = {
        Compare: _compare_to_query,
        Or: _or_to_query,
        And: _and_to_query,
        Not: _not_to_func,
    }
    for spec_type, convert in mapper.items():
        if isinstance(spec, spec_type):
            return convert(spec)

    return True


def _compare_to_query(spec: Compare) -> Any:
    mapper = {
        Operator.LE: operator.le,
        Operator.LT: operator.lt,
        Operator.GT: operator.gt,
        Operator.GE: operator.ge,
        Operator.EQ: operator.eq,
        Operator.NE: operator.ne,
    }
    op = mapper[spec.op]
    return op(_name_to_schema(spec.field), spec.value)


def _name_to_schema(name: str) -> Any:
    return {
        "code_id": schema.VerificationCode.code_id,
        "code": schema.VerificationCode.code,
        "telegram_id": schema.VerificationCode.telegram_id,
        "email": schema.VerificationCode.email,
        "used_at": schema.VerificationCode.used_at,
        "valid_until": schema.VerificationCode.valid_until,
        "created_at": schema.VerificationCode.created_at,
    }[name]


def _or_to_query(or_: Or) -> Any:
    args = [_spec_to_query(spec) for spec in or_.specs]
    return functools.reduce(operator.or_, args)


def _and_to_query(and_: And) -> Any:
    args = [_spec_to_query(spec) for spec in and_.specs]
    return functools.reduce(operator.and_, args)


def _not_to_func(not_: Not) -> Any:
    return not _spec_to_query(not_.spec)
