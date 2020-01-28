from __future__ import annotations

import random
from typing import List

import numpy as np

from push4.gp.evolution import GeneticAlgorithm
from push4.gp.selection import Lexicase
from push4.gp.simplification import GenomeSimplifier
from push4.gp.soup import CoreSoup
from push4.gp.spawn import Spawner, genome_to_push_code
from push4.gp.variation import size_neutral_umad, VariationSet
from push4.lang.dag import Dag

from push4.lang.expr import Constant, Input, Function
from push4.lang.push import Push
from push4.library.control import if_, _if_reifier


def target(lst: List[int]) -> List[int]:
    # The target function to evolve.
    return [i for i in lst if 100 >= i >= 0]


def random_input() -> List[int]:
    size = random.randint(0, 30)
    return [random.randint(-1000, 1000) for _ in range(size)]


x_train = [
    [-10, 0, 10, 100],
    [50, 40, 30, 20, 10, 0, -10],
    list(range(-1, 110, 5)),
    [2, 3, 4],
    [],
    [0, -1, -2, -3],
    [-1000, 1000],
    list(range(-10, 10)),
    list(range(90, 110)),
] + [random_input() for _ in range(50)]


# The penalty error to assign empty programs and programs which produce runtime errors.
penalty = 1e5


# The error function to guide evolution.
def error(program: Dag) -> np.array:
    errors = []
    for case in x_train:
        y_true = target(case)
        n_errors = len(y_true) + 1
        if program is None:
            errors += [penalty] * n_errors
        else:
            try:
                y_pred = program.eval(lst=case)
            except Exception as e:
                # print(e)
                errors += [penalty] * n_errors
                continue
            # Compare the outputs element-wise and compute absolute errors.
            for ndx, el_pred in enumerate(y_pred[:len(y_true)]):
                el_true = y_true[ndx]
                errors.append(abs(el_pred - el_true))
            # If y_pred is shorter than y_true, fill in missing elements with penalties.
            for _ in range(max(0, len(y_true) - len(y_pred))):
                errors.append(penalty)
            # Add the difference in size as an error.
            errors.append(abs(len(y_true) - len(y_pred)))
    return np.array(errors)


# The "soup" containing all expression which might appear in evolved programs.
soup = (
    CoreSoup()
    .register_constants([0, 100])
    .register_input("lst", List[int])
)


# The spawner which will generate random genes and genomes.
spawner = Spawner(soup)


# The parent selector.
selector = Lexicase(epsilon=False)


# The evolver
evo = GeneticAlgorithm(
    error_function=error,
    spawner=spawner,
    selector=selector,
    variation=VariationSet([
        (size_neutral_umad, 1.0),
        # (Alternation(), 0.2),
        # (Genesis(size=(10, 60)), 0.2),
    ]),
    population_size=1000,
    max_generations=300,
    initial_genome_size=(0, 50)
)


simplifier = GenomeSimplifier(error, List[int])


if __name__ == "__main__":
    best = evo.run(List[int])
    print(best.program.to_def("filter_in_range", ["lst"]))
    simp_best = simplifier.simplify(best)
    print(simp_best.program.to_def("filter_in_range", ["lst"]))

    # genome = [
    #     Constant(False),
    #     Constant(2),
    #     Input("lst", List[int]),
    #     Function(if_, _if_reifier)
    # ]
    #
    # push_code = genome_to_push_code(genome)
    #
    # prog = Push().compile(push_code, List[int], True)
    #
    # print()
    # prog.pprint()
    # print()
    # print(prog.to_def("filter_in_range", ["lst"]))
    # print()
    #
    # print(error(prog))
