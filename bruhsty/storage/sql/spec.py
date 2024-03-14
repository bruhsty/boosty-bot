import functools
import operator
from typing import Any, Callable, TypeAlias
from bruhsty.storage.specs import Specification, Compare, Or, And, Not, Operator

NameResolver: TypeAlias = Callable[[str], Any]


def spec_to_query(spec: Specification, resolve_name: NameResolver) -> Any:
    mapper = {
        Compare: compare_to_query,
        Or: _or_to_query,
        And: _and_to_query,
        Not: _not_to_func,
    }
    for spec_type, convert in mapper.items():
        if isinstance(spec, spec_type):
            return convert(spec, resolve_name)  # type: ignore

    return True


def compare_to_query(spec: Compare, resolve_name: NameResolver) -> Any:
    mapper = {
        Operator.LE: operator.le,
        Operator.LT: operator.lt,
        Operator.GT: operator.gt,
        Operator.GE: operator.ge,
        Operator.EQ: operator.eq,
        Operator.NE: operator.ne,
    }
    op = mapper[spec.op]
    return op(resolve_name(spec.field), spec.value)


def _or_to_query(or_: Or, resolve_name: NameResolver) -> Any:
    args = [spec_to_query(spec, resolve_name) for spec in or_.specs]
    return functools.reduce(operator.or_, args)


def _and_to_query(and_: And, resolve_name: NameResolver) -> Any:
    args = [spec_to_query(spec, resolve_name) for spec in and_.specs]
    return functools.reduce(operator.and_, args)


def _not_to_func(not_: Not, resolve_name: NameResolver) -> Any:
    return not spec_to_query(not_.spec, resolve_name)
