from typing import Sequence

from pyrsistent import pvector

import push4.interpreter as push


def int_add(a: int, b: int) -> int:
    return a + b


def int_mult(a: int, b: int) -> int:
    return a * b


def str_repeat(s: str, n: int) -> str:
    return s * n


def str_split(s: str, on: str) -> Sequence[str]:
    return pvector(s.split(on))


def first(seq: Sequence[str]) -> str:
    return seq[0]


genome = [
    int_add,
    " ",
    (0, "text", str),
    str_split,
    first,
    (1, "times", int),
    str_repeat,
    int_mult
]

if __name__ == "__main__":
    program = push.run(genome, str)

    program.pprint()
    print()

    a = program.eval("Hello World", 2)
    print(a)

    b = program.eval("Hi", 3)
    print(b)

    print()
    code = program.to_code("repeat_first_word", [("text", str), ("times", int)])
    print(code)
