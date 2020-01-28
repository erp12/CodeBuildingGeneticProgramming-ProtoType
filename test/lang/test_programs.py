from copy import copy
from typing import Sequence, Dict, Any

import pytest

from push4.gp.soup import CoreSoup
from push4.lang.expr import Function, Constant
from push4.lang.push import Push


def find_fn_exprs_in_soup(names: Sequence[str]) -> Dict[str, Function]:
    fn_exprs = {}
    for expr in CoreSoup().units:
        if isinstance(expr, Function) and expr.name in names:
            fn_exprs[expr.name] = copy(expr)
    return fn_exprs

