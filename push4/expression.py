import inspect
from abc import ABC
from typing import Sequence, Callable, Any, Mapping


class Expression(ABC):

    def __init__(self, name: str, return_type: type):
        self.name = name
        self.return_type = return_type

    def __repr__(self) -> str:
        return "{n}:{t}".format(n=self.name, t=clean_type_name(self.return_type))


class FunctionExpression(Expression):

    def __init__(self, name: str, return_type: type, input_types: Sequence[type], fn: Callable):
        super().__init__(name, return_type)
        self.input_types = input_types
        self.fn = fn

    def arity(self) -> int:
        return len(self.input_types)

    def __repr__(self) -> str:
        return "{n}({a})->{r}".format(
            n=self.name,
            a=",".join([clean_type_name(t) for t in self.input_types]),
            r=clean_type_name(self.return_type)
        )


class LiteralExpression(Expression):

    def __init__(self, value: Any):
        super().__init__(_constant_expression_name(value), type(value))
        self.value = value


class RegisterExpression(Expression):

    def __init__(self, position: int, name: str, data_type: type):
        super().__init__(name, data_type)
        self.position = position

    def __repr__(self):
        return "symbol:" + super().__repr__()


def expression_from_function(fn: Callable) -> FunctionExpression:
    signature = inspect.signature(fn)
    return FunctionExpression(
        name=fn.__name__,
        return_type=signature.return_annotation,
        input_types=[v.annotation for _, v in signature.parameters.items()],
        fn=fn
    )


def _constant_expression_name(value: Any) -> str:
    if isinstance(value, str):
        return "'{v}'".format(v=value)
    elif isinstance(value, Mapping):
        elms = ", ".join(
            ["{}: {}".format(_constant_expression_name(k), _constant_expression_name(v)) for k, v in value.items()])
        return "{" + elms + "}"
    elif isinstance(value, Sequence):
        return "[" + ", ".join([_constant_expression_name(el) for el in value]) + "]"
    # @TODO: What to do about instance objects?
    else:
        # Works for bool, int, float, bytes
        return str(value)


def clean_type_name(t: type) -> str:
    if t.__module__ == "typing":
        return str(t).lstrip("typing.")
    elif t.__module__ == "builtins":
        return t.__name__
    else:
        return t.__module__ + '.' + t.__qualname__
