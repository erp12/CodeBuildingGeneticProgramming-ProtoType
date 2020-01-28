import inspect
import random
from copy import deepcopy
from enum import Enum
from inspect import getmembers, isfunction, signature, _empty
from typing import Any, Callable, Mapping, List, Sequence, Tuple, Union, get_type_hints

from push4.library import functions, classes
from push4.lang.expr import Input, Constant, Function, Constructor, Expression, Method
from push4.lang.hof import FilterExpr, MapExpr, LocalInput
from push4.lang.reify import TypeReifier


class GeneToken(Enum):
    OPEN = 1
    CLOSE = 2


class ErcGenerator:

    def __init__(self, fn: Callable, type_override: type = None):
        n_args = len(inspect.signature(fn).parameters)
        assert n_args == 0, "ERC generator function must take no arguments."
        self.fn = fn
        self.type_override = type_override

    def create_constant(self) -> Constant:
        return Constant(self.fn(), self.type_override)


Unit = Union[Expression, GeneToken, ErcGenerator]


# @TODO: Add ERC generators?
class Soup:

    def __init__(self):
        self.units: List[Unit] = [
            GeneToken.OPEN,
            GeneToken.CLOSE
        ]

    def register_constant(self, value: Any, type_override: type = None):
        self.units.append(Constant(value, type_override))
        return self

    def register_constants(self, values: Sequence[Any], type_override: type = None):
        self.units = self.units + [Constant(v, type_override) for v in values]
        return self

    def register_input(self, name: str, typ: type):
        self.units.append(Input(name, typ))
        return self

    def register_function(self, fn: Callable, reifier: TypeReifier = None):
        self.units.append(Function(fn, reifier))
        return self

    def register_functions(self, fns: Sequence[Tuple[Callable, TypeReifier]]):
        self.units = self.units + [Function(f, r) for f, r in fns]
        return self

    def register_constructor(self, cls: type):
        self.units.append(Constructor(cls))
        return self

    def register_methods(self, cls: type, reifiers: Mapping[str, TypeReifier] = None):
        if reifiers is None:
            reifiers = {}
        for nm, fn in getmembers(cls, predicate=isfunction):
            ret = signature(fn).return_annotation
            if not (ret == _empty or nm.startswith("_")):
                self.units.append(Method(fn, reifiers.get(nm)))
        return self

    def register_class(self, cls: type):
        self.register_constructor(cls)
        self.register_methods(cls)
        return self

    def register_hofs(self):
        self.units.append(MapExpr())
        self.units.append(FilterExpr())
        self.units += [LocalInput(i) for i in range(3)]
        return self

    # @TODO: register_stack_instruction
    # @TODO: register_code_instruction

    def register_erc_generator(self, generator_fn: Callable):
        self.units.append(ErcGenerator(generator_fn))
        return self

    def random_unit(self) -> Expression:
        unit = random.choice(self.units)
        if isinstance(unit, ErcGenerator):
            unit = unit.create_constant()
        return deepcopy(unit)

    def random_units(self, k: int) -> List[Expression]:
        return [self.random_unit() for _ in range(k)]


def rand_float() -> float:
    return random.random()


def rand_int() -> int:
    return random.randint(-100, 100)


# @TODO: Random char ERC generator.


class CoreSoup(Soup):

    def __init__(self):
        super().__init__()
        for fn, reifier in functions:
            self.register_function(fn, reifier)
        for cls, reifier_dict in classes:
            self.register_methods(cls, reifier_dict)
            # self.register_class(cls)
        self.register_hofs()
        self.register_constants([-1, 0, 1, 2, 10, True, False])
        self.register_erc_generator(rand_float)
        self.register_erc_generator(rand_int)
