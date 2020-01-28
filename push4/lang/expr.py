from abc import ABC, abstractmethod
from copy import copy
from typing import Any, Callable, Type, get_type_hints, Mapping, Sequence, Dict

import numpy as np
from pyrsistent import pmap, v
from pytypes import is_subtype

from push4.collections import POMap
from push4.lang.node import Node
from push4.lang.reify import TypeReifier, NoopReifier, Signature, RequiredReifier


class Expression(Node, ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def dtype(self) -> type:
        ...

    @abstractmethod
    def arity(self) -> int:
        ...

    @abstractmethod
    def eval(self, **kwargs):
        ...

    @abstractmethod
    def to_code(self) -> str:
        ...

    @abstractmethod
    def to_form(self) -> str:
        ...

    def __repr__(self) -> str:
        nm = type(self).__name__
        body = self.to_form()
        if self.reified:
            body = self.to_code()
        return "{n}<{b}><dtype={t},depth={d}>".format(n=nm, b=body, t=self.dtype(), d=self.depth)


class Constant(Expression):

    def __init__(self, value: Any, type_override: type = None):
        super().__init__()
        self.value = value
        self._dtype = type_override
        if self._dtype is None:
            self._dtype = type(value)
        self.reify()

    def dtype(self) -> type:
        return self._dtype

    def arity(self) -> int:
        return 0

    def eval(self, **kwargs):
        return copy(self.value)

    def to_code(self) -> str:
        return self.to_form()

    def to_form(self) -> str:
        if isinstance(self.value, str):
            return "\"{v}\"".format(v=self.value)
        else:
            return str(self.value)

    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        return isinstance(other, Constant) and self.value == other.value


class Input(Expression):

    def __init__(self, symbol: str, dtype: type):
        super().__init__()
        self.symbol = symbol
        self._dtype = dtype
        self.reify()

    def dtype(self) -> type:
        return self._dtype

    def arity(self) -> int:
        return 0

    def eval(self, **kwargs):
        assert self.symbol in kwargs.keys(), "No input supplied for symbol " + self.symbol
        return kwargs[self.symbol]

    def to_code(self) -> str:
        return self.symbol

    def to_form(self) -> str:
        return self.symbol

    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        return isinstance(other, Input) and self.symbol == other.symbol and self.dtype() == other.dtype()


class FunctionLike(Expression, ABC):

    def __init__(self, name: str, fn: Callable, args: POMap, ret_type: type):
        super().__init__()
        self.name = name
        self.fn = fn
        self.base_signature = Signature.create({"ret": ret_type, "args": args})
        self.reified_signature = self.base_signature

    def dtype(self) -> type:
        return self.reified_signature.ret

    def args(self) -> POMap:
        return self.reified_signature.args

    def arity(self) -> int:
        return len(self.args())

    def eval(self, **kwargs):
        assert self.reified, "Cannot eval a Function expression that has not been reified."
        fn_kwargs = {name: child.eval(**kwargs) for name, child in self.children.items()}
        try:
            return self.fn(**fn_kwargs)
        except Exception as e:
            raise Exception("While evaluating {f} with {a} found {et}: {e}".format(
                f=self.fn, a=fn_kwargs, et=type(e).__name__, e=e
            ))

    def _validate_children(self):
        expected = set(self.args().keys())
        actual = set(self.children.keys())
        assert expected == actual, "Found incorrect arguments to Function {f}. Expected {e}. Found {a}.".format(
            f=self.name, e=expected, a=actual
        )
        for arg_name, child_expr in self.children.items():
            expected = self.args()[arg_name]
            actual = child_expr.dtype()
            check = is_subtype(actual, expected)
            if not check:
                print(self)
                print(self.args())
                print(self.children)
            assert check, \
                "Found incorrect {f} argument type for {arg}. Expected {e}. Got {a}.".format(
                    f=self.name, arg=arg_name, e=expected, a=actual
                )

    def _reify(self):
        if len(self.children) == self.arity():
            self._validate_children()

    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        return isinstance(other, FunctionLike) and self.reified_signature == other.reified_signature


_req_reifier = RequiredReifier()


class Function(FunctionLike):

    def __init__(self, fn: Callable, reifier: TypeReifier = None):
        type_hints = POMap()
        for nm, typ in get_type_hints(fn).items():
            type_hints = type_hints.add(nm, typ)

        ret = type_hints["return"]
        args = type_hints.discard("return")

        super().__init__(fn.__name__, fn, args, ret)

        self.reifier = reifier
        if reifier is None:
            self.reifier = NoopReifier()

    def to_code(self) -> str:
        assert self.reified, "Cannot format a Function as code that has not been reified."
        return "{name}({args})".format(
            name=self.name,
            args=", ".join([child.to_code() for child in self.children.values()])
        )

    def to_form(self) -> str:
        return "{name}({args})".format(name=self.name, args=", ".join(self.args().keys()))

    def _reify(self):
        super()._reify()
        children_dtypes = {name: child.dtype() for name, child in self.children.items()}
        sig = _req_reifier.reify(self.base_signature, children_dtypes)
        self.reified_signature = self.reifier.reify(sig, children_dtypes)

    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        return isinstance(other, Function) and self.name == other.name


class Method(Function):

    def to_code(self) -> str:
        self_arg = self.children["self"].to_code()
        other_children = self.children.discard("self")
        return "{slf}.{name}({args})".format(
            slf=self_arg,
            name=self.name,
            args=", ".join([child.to_code() for child in other_children.values()])
        )

    def to_form(self) -> str:
        non_self = self.args().discard("self")
        return "self.{name}({args})".format(name=self.name, args=", ".join(non_self.keys()))


class Constructor(FunctionLike):
    # @TODO: What do to about collections that require in-depth spec?

    def __init__(self, cls: type):
        self.cls = cls
        args = POMap()
        for arg_name, arg_type in get_type_hints(cls.__init__).items():
            if arg_name not in ["self", "return"]:
                args = args.add(arg_name, arg_type)
        super().__init__(cls.__name__, cls, args, cls)

    def to_code(self) -> str:
        assert self.reified, "Cannot format a Constructor as code that has not been reified."
        return "{name}({args})".format(
            name=self.name,
            args=", ".join([child.to_code() for child in self.children.values()])
        )

    def to_form(self) -> str:
        return "{name}({args})".format(name=self.name, args=", ".join(self.args().keys()))

    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        return isinstance(other, Constructor) and self.cls == other.cls


# class ControlFlow(Expression, ABC):
#
#     def __init__(self, body: Closure):
#         super().__init__()
#         self.body = body
#
#     @abstractmethod
#     def next(self, scope: Dict[str, Any], result: Any) -> Dict[str, Any]:
#         pass
#
#     @abstractmethod
#     def should_continue(self, scope: Dict[str, Any]) -> bool:
#         pass
#
#     @abstractmethod
#     def emit(self, final_scope: Dict[str, Any]) -> Dict[str, Any]:
#         pass
#
#     def eval(self, **kwargs):
#         scope = copy(kwargs)
#         scope.update({nm: child.eval(**kwargs) for nm, child in self.children.items()})
#         while self.should_continue(scope):
#             result = self.body.eval(**scope)
#             scope = self.next(scope, result)
#         self.emit(scope)
#
#
# class While(ControlFlow):
#     def next(self, scope: Dict[str, Any], result: Any) -> Dict[str, Any]:
#         pass
#
#     def should_continue(self, scope: Dict[str, Any]) -> bool:
#         pass
#
#     def emit(self, final_scope: Dict[str, Any]) -> Dict[str, Any]:
#         pass
#
#     def dtype(self) -> Type:
#         pass
#
#     def arity(self) -> int:
#         pass
#
#     def to_code(self) -> str:
#         pass
#
#     def to_form(self) -> str:
#         pass
#
#
# class For(ControlFlow):
#     def next(self, scope: Dict[str, Any], result: Any) -> Dict[str, Any]:
#         pass
#
#     def should_continue(self, scope: Dict[str, Any]) -> bool:
#         pass
#
#     def emit(self, final_scope: Dict[str, Any]) -> Dict[str, Any]:
#         pass
#
#     def dtype(self) -> Type:
#         pass
#
#     def arity(self) -> int:
#         pass
#
#     def to_code(self) -> str:
#         pass
#
#     def to_form(self) -> str:
#         pass
