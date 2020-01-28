from typing import List, Sequence, Any

import pytest

from push4.library.op import add
from push4.lang.expr import Constant, Input, Function, Constructor
from push4.lang.reify import RetToElementType, MaxTypeReifier


@pytest.fixture
def int_constant():
    return Constant(5)


@pytest.fixture
def int_constant():
    return Constant(5)


@pytest.fixture
def list_constant():
    return Constant(["a", "b", "c"], List[str])


@pytest.fixture
def input_expr():
    return Input("x", float)


@pytest.fixture
def add_fn():
    return Function(add, MaxTypeReifier([int, float]))


def first(seq: Sequence) -> Any:
    return seq[0]


@pytest.fixture
def first_fn():
    return Function(first, RetToElementType("seq"))


@pytest.fixture
def constructor():
    return Constructor(RetToElementType)
