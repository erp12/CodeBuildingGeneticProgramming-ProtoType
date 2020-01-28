from typing import Sequence

from push4.lang.expr import Input, Constant, Function
from push4.lang.push import Push


def int_add(a: int, b: int) -> int:
    return a + b


def int_mult(a: int, b: int) -> int:
    return a * b


def str_repeat(s: str, n: int) -> str:
    return s * n


def str_split(s: str, on: str) -> Sequence[str]:
    return s.split(on)


def first(seq: Sequence[str]) -> str:
    return seq[0]


if __name__ == "__main__":
    genome = [
        Constant(" "),
        Input("text", str),
        Function(str_split),
        Constant(False),
        Function(first),
        Input("times", int),
        Function(str_repeat),
        Function(int_add),
    ]
    print("Genome:", genome)

    program = Push().compile(genome, str, True)
    print()
    print("Output type:", program.return_type())
    print()
    program.pprint()

    print()
    print("Testing Program")
    print(program.eval(text="Hello Wolrd", times=3))

    print()
    print("Program As Python")
    print(program.to_def("repeat_first_word", ["text", "times"]))
