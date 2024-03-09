import dataclasses
import operator
from datetime import datetime, timedelta
from typing import Callable, AsyncIterable

from ..errors import CodeNotFoundError
from ..models import Code, EditableFields
from bruhsty.storage.specs import (
    Specification, Compare, Or,
    Not, And, Operator, Field
)


class CodeField:
    CODE_ID = Field("code_id")
    TELEGRAM_ID = Field("telegram_id")
    EMAIL = Field("email")
    CODE = Field("code")
    CREATED_AT = Field("created_at")
    USED_AT = Field("used_at")
    VALID_UNTIL = Field("valid_until")


class CodeStorage:
    def __init__(self, code_ttl: timedelta) -> None:
        self.code_ttl = code_ttl
        self._last_code_id = 0
        self._storage = dict[int, Code]()

    async def add(self, telegram_id: int, email: str, code: str) -> Code:
        self._last_code_id += 1
        now = datetime.now()
        code = Code(
            code_id=self._last_code_id,
            code=code,
            telegram_id=telegram_id,
            email=email,
            created_at=now,
            valid_until=now + self.code_ttl,
            used_at=None,
        )
        self._storage[code.code_id] = code
        return dataclasses.replace(code)

    async def update(self, code_id: int, **updates: EditableFields) -> Code:
        if code_id not in self._storage:
            raise CodeNotFoundError(code_id, f"code with id {code_id} does not exist")

        self._storage[code_id] = dataclasses.replace(self._storage[code_id], **updates)

        return dataclasses.replace(self._storage[code_id])

    async def find(self, spec: Specification) -> AsyncIterable[Code]:
        func = _spec_to_func(spec)
        for code in self._storage.values():
            if func(code):
                yield code


def _spec_to_func(spec: Specification) -> Callable[[Code], bool]:
    mapper = {
        Compare: _compare_to_func,
        Or: _or_to_func,
        And: _and_to_func,
        Not: _not_to_func,
    }
    for spec_type, convert in mapper.items():
        if isinstance(spec, spec_type):
            return convert(spec)

    return lambda code: True


def _compare_to_func(spec: Compare) -> Callable[[Code], bool]:
    mapper = {
        Operator.LE: operator.le,
        Operator.LT: operator.lt,
        Operator.GT: operator.gt,
        Operator.GE: operator.ge,
        Operator.EQ: operator.eq,
        Operator.NE: operator.ne,
    }
    op = mapper[spec.op]
    return lambda code: op(getattr(code, spec.field, None), spec.value)


def _or_to_func(or_: Or) -> Callable[[Code], bool]:
    funcs = [_spec_to_func(spec) for spec in or_.specs]
    return lambda code: any(f(code) for f in funcs)


def _and_to_func(and_: And) -> Callable[[Code], bool]:
    funcs = [_spec_to_func(spec) for spec in and_.specs]
    return lambda code: all(f(code) for f in funcs)


def _not_to_func(not_: Not) -> Callable[[Code], bool]:
    return lambda code: not _spec_to_func(not_.spec)(code)
