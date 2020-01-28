from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Any, Set, Sequence, Tuple, List

from pyrsistent import v, pvector
from pytypes import is_subtype

from push4.lang.expr import Expression, Input


def all_nodes_of_type(expr: Expression, cls: type) -> Set:
    nodes = set()
    if isinstance(expr, cls):
        nodes.add(expr)
    for c in expr.children:
        nodes.union(all_nodes_of_type(c, cls))
    return nodes


class LocalInput(Input):

    def __init__(self, ndx: int, typ: type = Any):
        super().__init__("_" + str(ndx), typ)
        self.ndx = ndx


class Closure:

    def __init__(self, func_def: Sequence[Expression]):
        self.func_def = pvector(func_def)

    def __repr__(self) -> str:
        return str(self.func_def)


class HOF(Expression, ABC):

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    @abstractmethod
    def inner_func_spec(self) -> Tuple[int, type]:
        pass

    def arity(self) -> int:
        return 2  # Always "seq" and "body".

    def _validate_children(self):
        assert set(self.children.keys()) == {"seq", "func"}, "Children of HoF expressions must be 'seq' and 'func'."
        assert is_subtype(self.children["seq"].dtype(), List), "Seq child of HoF must return List."

    def _reify(self):
        self._validate_children()


class MapExpr(HOF):

    def __init__(self):
        super().__init__("map")
        self._dtype = List

    def inner_func_spec(self) -> Tuple[int, type]:
        return 1, Any

    def dtype(self) -> type:
        return self._dtype

    def eval(self, **kwargs):
        seq: List = self.children["seq"].eval(**kwargs)
        func: Expression = self.children["func"]
        result = []
        for el in seq:
            scope = {"_0": el}
            scope.update(kwargs)
            result.append(func.eval(**scope))
        return result

    def to_code(self) -> str:
        assert self.reified, "Cannot format a HoF expression as code that has not been reified."
        return "map(lambda _0: {b}, {s})".format(
            n=self.name,
            b=self.children["func"].to_code(),
            s=self.children["seq"].to_code()
        )

    def to_form(self) -> str:
        return "map(lambda _0: func(_0), seq)".format(n=self.name)

    def _reify(self):
        super()._reify()
        self._dtype = List[self.children["func"].dtype()]


class FilterExpr(HOF):

    def __init__(self):
        super().__init__("filter")
        self._dtype = List

    def inner_func_spec(self) -> Tuple[int, type]:
        return 1, bool

    def dtype(self) -> type:
        return self._dtype

    def eval(self, **kwargs):
        seq: List = self.children["seq"].eval(**kwargs)
        body: Expression = self.children["func"]
        result = []
        for el in seq:
            scope = {"_0": el}
            scope.update(kwargs)
            if body.eval(**scope):
                result.append(el)
        return result

    def to_code(self) -> str:
        assert self.reified, "Cannot format a HoF expression as code that has not been reified."
        return "filter(lambda _0: {b}, {s})".format(
            n=self.name,
            b=self.children["func"].to_code(),
            s=self.children["seq"].to_code()
        )

    def to_form(self) -> str:
        return "filter(lambda _0: func(_0), seq)".format(n=self.name)

    def _reify(self):
        super()._reify()
        self._dtype = self.children["seq"].dtype()
