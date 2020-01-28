from __future__ import annotations

import typing as t
import pytypes as pt

from pathlib import Path


def fn(x: int, s: str, **kwargs) -> t.List[str]:
    return [s] * x


if __name__ == "__main__":
    print(t.get_type_hints(fn))
    print(pt.get_type_hints(fn))
