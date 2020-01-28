import pytest

from push4.lang.dag import Dag


@pytest.fixture
def simple_dag(add_fn, int_constant, input_expr):
    root = add_fn.add_children({"a": int_constant, "b": input_expr})
    return Dag(root)


class TestDag:

    def test_eval(self, simple_dag):
        assert simple_dag.eval(x=0.5) == 5.5
        assert simple_dag.eval(x=-5.0) == 0.0

    def test_return_type(self, simple_dag):
        assert simple_dag.return_type() == float

    def test_to_code(self, simple_dag):
        assert simple_dag.to_code() == "add(5, x)"

    def test_to_def(self, simple_dag):
        assert simple_dag.to_def("plus_5", ["x"]) == "def plus_5(x):\n    return add(5, x)"

    def test_pprint(self, simple_dag, capsys):
        simple_dag.pprint()
        captured = capsys.readouterr()
        assert captured.out == ("- Function<add(5, x)><dtype=<class 'float'>,depth=2>\n"
                                "| - Constant<5><dtype=<class 'int'>,depth=1>\n"
                                "| - Input<x><dtype=<class 'float'>,depth=1>\n")
