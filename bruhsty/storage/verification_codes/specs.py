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


@dataclass
class Field(Generic[T, FieldType]):
    field: FieldType

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

    def __neq__(self, value: T) -> Compare:
        return Compare(Operator.LE, self.field, value)


@dataclass
class Compare(Generic[T, FieldType], Specification):
    op: Operator
    field: FieldType
    value: T
