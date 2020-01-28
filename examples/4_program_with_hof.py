from typing import List

from push4.gp.soup import GeneToken
from push4.gp.spawn import genome_to_push_code
from push4.lang.expr import Input, Function
from push4.lang.hof import LocalInput, MapExpr, FilterExpr
from push4.lang.push import Push


def int_inc(a: int) -> int:
    return a + 1


def odd(a: int) -> bool:
    return a % 2 == 1


if __name__ == "__main__":
    genome = [
        Input("my_list", List[int]),
        GeneToken.OPEN,
        LocalInput(0),
        Function(int_inc),
        GeneToken.CLOSE,
        MapExpr(),
        GeneToken.OPEN,
        LocalInput(0),
        Function(odd),
        GeneToken.CLOSE,
        FilterExpr(),
    ]
    print("Genome:", genome)
    print()

    push_code = genome_to_push_code(genome)
    print("Push Code:", push_code)
    print()

    program = Push().compile(push_code, List[int], True)
    print()
    program.pprint()
    print()
    print("Output type:", program.return_type())

    print()
    print("Testing Program")
    print(program.eval(my_list=[5, 10, 15]))
    print(program.eval(my_list=[-10, 0, 10]))

    print()
    print("Program As Python")
    print(program.to_def("inc_then_odds", ["my_list"]))
