from __future__ import annotations

from typing import List, Sequence


class String(str):

    def capitalize(self: str) -> str:
        return str.capitalize(self)

    def count(self: str, sub: str) -> int:
        return str.count(self, sub)

    def endswith(self: str, suffix: str) -> bool:
        return str.endswith(self, suffix)

    def find(self: str, sub: str) -> int:
        # @NOTE: Use `find` instead of `index` to avoid runtime error.
        return str.find(self, sub)

    def isalnum(self: str) -> bool:
        return str.isalnum(self)

    def isalpha(self: str) -> bool:
        return str.isalnum(self)

    def isascii(self: str) -> bool:
        return str.isascii(self)

    def isdecimal(self: str) -> bool:
        return str.isdecimal(self)

    def isdigit(self: str) -> bool:
        return str.isdigit(self)

    def isidentifier(self: str) -> bool:
        return str.isidentifier(self)

    def islower(self: str) -> bool:
        return str.islower(self)

    def isnumeric(self: str) -> bool:
        return str.isnumeric(self)

    def isprintable(self: str) -> bool:
        return str.isprintable(self)

    def isspace(self: str) -> bool:
        return str.isspace(self)

    def istitle(self: str) -> bool:
        return str.istitle(self)

    def isupper(self: str) -> bool:
        return str.isupper(self)

    def join(self: str, iterable: Sequence) -> str:
        return str.join(self, iterable)

    def lower(self: str) -> str:
        return str.lower(self)

    def lstrip(self: str, chars: str = None) -> str:
        return str.lstrip(chars)

    def lstrip_ws(self: str) -> str:
        return self.lstrip()

    def replace(self: str, old: str, new: str, count: int = -1) -> str:
        return str.replace(self, old, new, count)

    def replace_all(self: str, old: str, new: str) -> str:
        return self.replace(old, new)

    def rfind(self: str, sub: str) -> int:
        return str.rfind(sub)

    def rstrip(self: str, chars: str = None) -> str:
        return str.rstrip(chars)

    def rstrip_ws(self: str):
        return self.rstrip()

    def split(self: str, sep: str = None) -> List[str]:
        return [part for part in str.split(self, sep)]

    def split_ws(self: str) -> List[str]:
        return self.split(self)

    def splitlines(self: str) -> List[str]:
        return [line for line in str.splitlines(self)]

    def startswith(self: str, prefix: str) -> bool:
        return str.startswith(self, prefix)

    def strip(self: str, chars: str = None) -> str:
        return str.strip(chars)

    def strip_ws(self: str) -> str:
        return self.strip(self)

    def swapcase(self: str) -> str:
        return str.swapcase(self)

    def title(self: str) -> str:
        return str.title(self)

    def upper(self: str) -> str:
        return str.upper(self)


String_reifiers = {}


def add(s1: str, s2: str) -> str:
    return s1 + s2


def in_(key: str, string: str) -> bool:
    return key in string


def eq(s1: str, s2: str) -> bool:
    return s1 == s2


def getitem(s1: str, ndx: int) -> str:
    return s1[ndx]


def ge(s1: str, s2: str) -> bool:
    return s1 >= s2


def gt(s1: str, s2: str) -> bool:
    return s1 > s2


def len_(s: str) -> int:
    return len(s)


def le(s1: str, s2: str) -> bool:
    return s1 <= s2


def lt(s1: str, s2: str) -> bool:
    return s1 < s2


def mul(s: str, i: int) -> str:
    return s * i


def ne(s1: str, s2: str) -> bool:
    return s1 != s2


fns = [
    (add, None),
    (in_, None),
    (eq, None),
    (getitem, None),
    (ge, None),
    (gt, None),
    (len_, None),
    (le, None),
    (lt, None),
    (mul, None),
    (ne, None)
]
