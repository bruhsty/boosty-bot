import operator

import pytest

from bruhsty.storage.specs import And, Compare, Field, Operator, Or


class MyClass:
    int_field = Field[int]()
    str_field = Field[str]("another_name")

    def __init__(self, int_value: int, str_value: str) -> None:
        self.int_field = int_value
        self.str_field = str_value


def test_field_get_value():
    my = MyClass(1, "abc")
    my.int_field = 1
    my.str_field = "abc"
    # Should return value when called on object
    assert my.int_field == 1
    assert my.str_field == "abc"

    # Should return itself when called on class
    assert isinstance(MyClass.int_field, Field)
    assert isinstance(MyClass.str_field, Field)

    # Should correctly set its name
    assert MyClass.int_field.field == "int_field"
    assert MyClass.str_field.field == "another_name"


operators = [
    operator.eq,
    operator.ne,
    operator.le,
    operator.lt,
    operator.ge,
    operator.gt,
]


@pytest.mark.parametrize("op", operators)
def test_field_comparison_operator(op):
    mapper = {
        Operator.LE: operator.le,
        Operator.LT: operator.lt,
        Operator.GT: operator.gt,
        Operator.GE: operator.ge,
        Operator.EQ: operator.eq,
        Operator.NE: operator.ne,
    }
    query = op(MyClass.str_field, "str value")
    assert isinstance(query, Compare)
    assert query.field == MyClass.str_field.field
    assert query.value == "str value"
    assert mapper[query.op] == op


def test_field_logical_operator():
    s1 = MyClass.str_field == "123"
    s2 = MyClass.str_field == "456"
    s3 = MyClass.str_field == "567"

    assert s1 & s2 == And([s1, s2])
    assert s1 | s2 == Or([s1, s2])

    assert s1 & s2 & s3 == And([And([s1, s2]), s3])
    assert s1 & s2 | s3 == Or([And([s1, s2]), s3])
