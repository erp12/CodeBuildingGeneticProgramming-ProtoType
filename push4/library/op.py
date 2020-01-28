import operator as op
from typing import Union, Any, Sequence, Collection, List

from push4.lang.reify import PassThroughReifier, MaxTypeReifier, RetToElementType, ArgsToSame

Numeric = Union[int, float]
Comparable = Union[Numeric, str]


# Comparison Operations *******************************************************#

def lt(a: Comparable, b: Comparable) -> bool:
    return op.lt(a, b)


def le(a: Comparable, b: Comparable) -> bool:
    return op.le(a, b)


def eq(a: Any, b: Any) -> bool:
    return op.eq(a, b)


def ne(a: Any, b: Any) -> bool:
    return op.ne(a, b)


def ge(a: Comparable, b: Comparable) -> bool:
    return op.ge(a, b)


def gt(a: Comparable, b: Comparable) -> bool:
    return op.gt(a, b)


# Logical Operations **********************************************************#


def not_(a: bool) -> bool:
    return op.not_(a)


def and_(a: bool, b: bool) -> bool:
    return a and b


def or_(a: bool, b: bool) -> bool:
    return a or b


# Mathematical/Bitwise Operations *********************************************#


def abs_(a: Numeric) -> Numeric:
    return abs(a)


def add(a: Numeric, b: Numeric) -> Numeric:
    return op.add(a, b)


def floordiv(a: Numeric, b: Numeric) -> float:
    if b == 0:
        return 0.0
    return op.floordiv(a, b)


def mod(a: Numeric, b: Numeric) -> Numeric:
    if b == 0:
        return 0.0
    return op.mod(a, b)


def mul(a: Numeric, b: Numeric) -> Numeric:
    return op.mul(a, b)


def neg(a: Numeric) -> Numeric:
    return op.neg(a)


def pos(a: Numeric) -> Numeric:
    return op.pos(a)


# def pow(a: Numeric, b: Numeric) -> Numeric:
#     return op.pow(a, b)


def sub(a: Numeric, b: Numeric) -> Numeric:
    return op.sub(a, b)


def div(a: Numeric, b: Numeric) -> float:
    if b == 0:
        return 0.0
    return op.truediv(a, b)


# Numbers *********************************************************#


def round_(number: Numeric, ndigits: int) -> Numeric:
    return round(number, ndigits)


# Collect *********************************************************#


def min_(a: Numeric, b: Numeric) -> Numeric:
    return min(a, b)


def max_(a: Numeric, b: Numeric) -> Numeric:
    return max(a, b)


def sum_(coll: List[Numeric]) -> Numeric:
    return sum(coll)


# Export *********************************************************#


_b_same_as_a = ArgsToSame("a", {"b"})
_pass_through_a = PassThroughReifier("a")
_max_numeric = MaxTypeReifier([int, float])

fns = [
    (lt, _b_same_as_a),
    (le, _b_same_as_a),
    (eq, None),
    (ne, None),
    (ge, _b_same_as_a),
    (gt, _b_same_as_a),
    (not_, None),
    (and_, None),
    (or_, None),
    (abs_, _pass_through_a),
    (add, _max_numeric),
    (floordiv, None),
    (mod, _max_numeric),
    (mul, _max_numeric),
    (neg, _pass_through_a),
    (pos, _pass_through_a),
    (sub, _max_numeric),
    (div, None),
    (round_, _max_numeric),
    (min_, _max_numeric),
    (max_, _max_numeric),
    (sum_, RetToElementType("coll"))
]
