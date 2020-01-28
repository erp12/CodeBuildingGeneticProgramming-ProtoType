from typing import Any

from push4.lang.reify import ReifierChain, PassThroughReifier, ArgsToSame


def if_(cond: bool, then: Any, else_: Any) -> Any:
    if cond:
        return then
    else:
        return else_


_if_reifier = ReifierChain([
    ArgsToSame("then", {"else_"}),
    PassThroughReifier("then")
])


fns = [
    (if_, _if_reifier)
]
