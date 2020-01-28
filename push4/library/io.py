from typing import Any

from push4.lang.reify import PassThroughReifier


def print_tap(to_do: Any) -> Any:
    print(to_do, end="")
    return to_do


def println_tap(to_do: Any) -> Any:
    print(to_do)
    return to_do


def print_do(to_print: Any, to_do: Any) -> Any:
    print(to_print, end="")
    return to_do


def do_print(to_do: Any, to_print: Any) -> Any:
    print(to_print, end="")
    return to_do


_pass_do = PassThroughReifier("to_do")

fns = [
    (print_tap, _pass_do),
    (println_tap, _pass_do),
    (print_do, _pass_do),
    (do_print, _pass_do),
]
