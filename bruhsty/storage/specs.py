from __future__ import annotations

import abc
import enum
from dataclasses import dataclass
from typing import Generic, TypeVar

__all__ = ["Operator", "Specification", "And", "Or", "Not", "Compare", "Field"]

T = TypeVar('T')


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
        return Or([self, other])

    def __and__(self, other: Specification) -> Specification:
        return And([self, other])


@dataclass
class And(Specification):
    specs: list[Specification]


@dataclass
class Or(Specification):
    specs: list[Specification]


@dataclass
class Not(Specification):
    spec: Specification


FieldType = TypeVar('FieldType')


class Field[T]:

    def __init__(self, field_name: str | None = None) -> None:
        self.field = field_name
        self.value: T | None = None

    def __get__(self, obj: object | None, obj_type=None) -> T:
        if obj is None:
            return self
        else:
            return self.value

    def __set_name__(self, owner, name: str):
        if self.field == "" or self.field is None:
            self.field = name

    def __set__(self, instance, value: T):
        self.value = value

    def __le__(self, value: T) -> Compare:
        return Compare(Operator.LE, self.field, value)

    def __lt__(self, value: T) -> Compare:
        return Compare(Operator.LT, self.field, value)

    def __gt__(self, value: T) -> Compare:
        return Compare(Operator.GT, self.field, value)

    def __ge__(self, value: T) -> Compare:
        return Compare(Operator.GE, self.field, value)

    def __eq__(self, value: T) -> Compare:
        return Compare(Operator.EQ, self.field, value)

    def __ne__(self, value: T) -> Compare:
        return Compare(Operator.NE, self.field, value)


@dataclass
class Compare(Generic[T, FieldType], Specification):
    op: Operator
    field: FieldType
    value: T
