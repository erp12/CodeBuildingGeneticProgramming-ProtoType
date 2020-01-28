from typing import Any


def str_(a: Any) -> str:
    return str(a)


def int2float(i: int) -> float:
    return float(i)


def float2int(f: float) -> int:
    return int(f)


def int2bool(i: int) -> bool:
    return bool(i)


def float2bool(f: float) -> bool:
    return bool(f)


def bool2int(b: bool) -> int:
    return int(b)


def bool2float(b: bool) -> float:
    return float(b)


# def str2int(s: str) -> int:
#     return int(s)
#
#
# def str2float(s: str) -> float:
#     return float(s)


# Export *********************************************************#

fns = [
    (str_, None),
    (int2float, None),
    (float2int, None),
    (int2bool, None),
    (float2bool, None),
    (bool2int, None),
    (bool2float, None),
    # (str2int, None),
    # (str2float, None),
]
