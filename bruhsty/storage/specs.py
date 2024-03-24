from __future__ import annotations

import abc
import enum
from dataclasses import dataclass
from types import EllipsisType
from typing import Any, Generic, TypeVar, overload

__all__ = ["Operator", "Specification", "And", "Or", "Not", "Compare", "Field"]

T = TypeVar("T")


class Operator(str, enum.Enum):
    LT = "lt"
    GT = "gt"
    GE = "ge"
    LE = "le"
    EQ = "eq"
    NE = "ne"


class Specification(abc.ABC):
    def __neg__(self) -> Specification:
        return Not(self)

    def __or__(self, other: Specification) -> Specification:
        return Or(self, other)

    def __and__(self, other: Specification) -> Specification:
        return And(self, other)


class And(Specification):
    def __init__(self, *specs: Specification) -> None:
        self.specs = specs


class Or(Specification):
    def __init__(self, *specs: Specification) -> None:
        self.specs = specs


class Not(Specification):
    def __init__(self, spec: Specification) -> None:
        self.spec = spec


FieldType = TypeVar("FieldType")


class Field(Generic[T]):
    def __init__(self, default: T | EllipsisType = ..., field_name: str | None = None) -> None:
        self.field = field_name
        self.value = default

    @overload
    def __get__(self, obj: None, owner: Any) -> T: ...

    @overload
    def __get__(self, obj: object, owner: Any) -> Field[T]: ...

    def __get__(self, obj: object | None, owner: Any) -> T | Field[T]:
        if obj is None:
            return self
        else:
            if isinstance(self.value, EllipsisType):
                raise AttributeError(f"Field {self.field} was not set and has no default value")
            return self.value

    def __set_name__(self, owner, name: str):
        if self.field == "" or self.field is None:
            self.field = name

    def __set__(self, instance, value: T):
        self.value = value

    def __le__(self, value: T) -> Compare:
        return Compare(Operator.LE, self.field or "", value)

    def __lt__(self, value: T) -> Compare:
        return Compare(Operator.LT, self.field or "", value)

    def __gt__(self, value: T) -> Compare:
        return Compare(Operator.GT, self.field or "", value)

    def __ge__(self, value: T) -> Compare:
        return Compare(Operator.GE, self.field or "", value)

    def __eq__(self, value: T) -> Compare:  # type: ignore
        return Compare(Operator.EQ, self.field or "", value)

    def __ne__(self, value: T) -> Compare:  # type: ignore
        return Compare(Operator.NE, self.field or "", value)


@dataclass
class Compare(Generic[T], Specification):
    op: Operator
    field: str
    value: T
