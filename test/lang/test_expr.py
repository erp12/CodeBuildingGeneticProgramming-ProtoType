from copy import copy
from typing import List, Any, Union

import pytest

from push4.lang.expr import Constant, Function
from push4.lang.reify import RetToElementType


class TestConstant:

    def test_dtype(self, int_constant, list_constant):
        assert int_constant.dtype() == int
        assert list_constant.dtype() == List[str]

    def test_eval(self, int_constant, list_constant):
        assert int_constant.eval() == 5
        assert list_constant.eval() == ["a", "b", "c"]

    def test_to_form(self, int_constant, list_constant):
        assert int_constant.to_form() == "5"
        assert list_constant.to_form() == "['a', 'b', 'c']"


class TestInput:

    def test_dtype(self, input_expr):
        assert input_expr.dtype() == float

    def test_eval(self, input_expr):
        assert input_expr.eval(x=1.0, b=True) == 1.0
        with pytest.raises(AssertionError):
            input_expr.eval()

    def test_to_form(self, input_expr):
        assert input_expr.to_form() == "x"


@pytest.fixture
def reified_first_fn(first_fn: Function, list_constant: Constant) -> Function:
    expr = copy(first_fn).add_child("seq", list_constant)
    expr.reify()
    return expr


class TestFunction:

    def test_dtype(self, add_fn, first_fn, reified_first_fn):
        assert add_fn.dtype() == Union[int, float]
        assert first_fn.dtype() == Any
        assert reified_first_fn.dtype() == str

    def test_eval(self, add_fn, first_fn, reified_first_fn):
        assert reified_first_fn.eval() == "a"

    def test_to_form(self, add_fn, first_fn):
        assert add_fn.to_form() == "add(a, b)"
        assert first_fn.to_form() == "first(seq)"

    def test_to_code(self, reified_first_fn):
        assert reified_first_fn.to_code() == "first(['a', 'b', 'c'])"


class TestConstructor:

    def test_dtype(self, constructor):
        assert constructor.dtype() == RetToElementType

    def test_eval(self, constructor):
        constructor.add_child("collection_arg_name", Constant("coll"))
        constructor.reify()
        assert isinstance(constructor.eval(), RetToElementType)

    def test_to_form(self, constructor):
        assert constructor.to_form() == "RetToElementType(collection_arg_name)"
