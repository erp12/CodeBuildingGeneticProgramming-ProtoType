from copy import copy
from typing import Union, Any

import pytest

from push4.lang.dag import Dag
from push4.lang.expr import Constant
from push4.lang.push import PushStack, Push


class TestPushStack:

    def test_push(self):
        stack = PushStack()
        stack.push(5).push("A")
        assert list(stack) == [5, "A"]

    def test_nth(self):
        stack = PushStack()
        stack.push(5).push(4).push(3)
        assert stack.nth(1) == 4

    def test_nth_oob(self):
        stack = PushStack()
        stack.push(5)
        assert stack.nth(1) is None

    def test_top(self):
        stack = PushStack()
        stack.push(5).push(-10)
        assert stack.top() == -10

    def test_top_of_empty(self):
        assert PushStack().top() is None

    def test_insert(self):
        stack = PushStack().push("a").push("b").push("c").insert(1, "z")
        assert list(stack) == ["a", "b", "z", "c"]

    def test_insert_oob(self):
        stack = PushStack().push("a").push("b").push("c").insert(10, "z")
        assert list(stack) == ["z", "a", "b", "c"]

    def test_set_nth(self):
        stack = PushStack().push("a").push("b").push("c").push("d").set_nth(1, "z")
        assert list(stack) == ["a", "b", "z", "d"]

    def test_set_nth_oob(self):
        with pytest.raises(IndexError):
            PushStack().push("a").push("b").push("c").set_nth(10, "z")

    def test_flush(self):
        stack = PushStack().push(1).push(-1).flush()
        assert len(stack) == 0


class TestPush:

    def test_pop_top_literal_simple_type(self):
        push = Push()
        push.dag_stack.push(Constant(7)).push(Constant("A"))
        top_int = push._pop_top_valid(int)
        assert top_int == Constant(7)
        assert list(push.dag_stack) == [Constant("A")]

        top_list = push._pop_top_valid(list)
        assert top_list is None
        assert list(push.dag_stack) == [Constant("A")]

    def test_pop_top_literal_union_type(self):
        push = Push()
        push.dag_stack.push(Constant(7)).push(Constant("A"))
        top_int = push._pop_top_valid(Union[int, float])
        assert top_int == Constant(7)
        assert list(push.dag_stack) == [Constant("A")]

        top_list = push._pop_top_valid(Union[list, Any])
        assert top_list == Constant("A")
        assert list(push.dag_stack) == []

    def test_pop_children(self):
        push = Push()
        push.dag_stack.push(Constant(7)).push(Constant("A"))
        children = push._pop_children({"n": Union[int, float], "s": str})
        assert children == {"n": Constant(7), "s": Constant("A")}
        assert list(push.dag_stack) == []

    def test_pop_children_not_enough(self):
        push = Push()
        push.dag_stack.push(Constant(7))
        children = push._pop_children({"n": Union[int, float], "s": str})
        assert children is None
        assert list(push.dag_stack) == [Constant(7)]

    def test_pop_children_wrong_types(self):
        push = Push()
        push.dag_stack.push(Constant(7)).push(Constant("A"))
        children = push._pop_children({"l": list, "s": str})
        assert children is None
        assert list(push.dag_stack) == [Constant(7), Constant("A")]

    def test_process_expr(self, add_fn, int_constant, input_expr):
        push = Push()
        push.process_expr(input_expr)
        assert list(push.dag_stack) == [input_expr]

        push.process_expr(int_constant)
        assert list(push.dag_stack) == [input_expr, int_constant]

        push.process_expr(add_fn)
        expected = copy(add_fn)
        expected.add_children({"a": int_constant, "b": input_expr})
        expected.reify()
        assert list(push.dag_stack) == [expected]

    def test_compile(self, int_constant, input_expr, add_fn):
        push_code = [int_constant, input_expr, add_fn]
        push = Push()
        dag = push.compile(push_code, float)

        expected = copy(add_fn)
        expected.add_children({"a": input_expr, "b": int_constant})
        expected.reify()

        assert dag == Dag(expected)
        assert dag.return_type() == float

