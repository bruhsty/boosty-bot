import operator

import pytest

from bruhsty.storage.specs import Field, Compare, Operator, And, Or


class Test:
    int_field = Field[int]()
    str_field = Field[str]("another_name")

    def __init__(self, int_value: int, str_value: str) -> None:
        self.int_field = int_value
        self.str_field = str_value


def test_field_get_value():
    t = Test(1, "abc")
    t.int_field = 1
    t.str_field = "abc"
    # Should return value when called on object
    assert t.int_field == 1
    assert t.str_field == "abc"

    # Should return itself when called on class
    assert isinstance(Test.int_field, Field)
    assert isinstance(Test.str_field, Field)

    # Should correctly set its name
    assert Test.int_field.field == "int_field"
    assert Test.str_field.field == "another_name"


operators = [
    operator.eq, operator.ne,
    operator.le, operator.lt,
    operator.ge, operator.gt,
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
    query = op(Test.str_field, "str value")
    assert isinstance(query, Compare)
    assert query.field == Test.str_field.field
    assert query.value == "str value"
    assert mapper[query.op] == op


def test_field_logical_operator():
    s1 = Test.str_field == "123"
    s2 = Test.str_field == "456"
    s3 = Test.str_field == "567"

    assert s1 & s2 == And([s1, s2])
    assert s1 | s2 == Or([s1, s2])

    assert s1 & s2 & s3 == And([And([s1, s2]), s3])
    assert s1 & s2 | s3 == Or([And([s1, s2]), s3])

