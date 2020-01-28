from __future__ import annotations

import random
from typing import List

import numpy as np

from push4.gp.evolution import GeneticAlgorithm
from push4.gp.selection import Lexicase
from push4.gp.simplification import GenomeSimplifier
from push4.gp.soup import CoreSoup
from push4.gp.spawn import Spawner
from push4.gp.variation import size_neutral_umad, VariationSet
from push4.lang.dag import Dag


def target(lst: List[int]) -> int:
    # The target function to evolve.
    return sum([i + 1 for i in lst])


def random_input() -> List[int]:
    size = random.randint(0, 30)
    return [random.randint(-1000, 1000) for _ in range(size)]


x_train = [
    [0, 1],
    [1],
    [-10, 10, 100],
    [50, 40, 30, 20, 10, 0, -10],
    list(range(-1, 110, 5)),
    [2, 3, 4],
    [],
    [-1, -2, -3],
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
        if program is None:
            errors.append(penalty)
        else:
            try:
                y_pred = program.eval(lst=case)
                errors.append(abs(y_true - y_pred))
            except Exception as e:
                # print(e)
                errors.append(penalty)
    return np.array(errors)


# The "soup" containing all expression which might appear in evolved programs.
soup = CoreSoup().register_input("lst", List[int])

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
        # (Genesis(size=(50, 50)), 1.0),
    ]),
    population_size=1000,
    max_generations=300,
    initial_genome_size=(5, 30)
)

simplifier = GenomeSimplifier(error, int)

if __name__ == "__main__":
    best = evo.run(int)
    print(best.program.to_def("sum_increments", ["lst"]))
    simp_best = simplifier.simplify(best)
    print(simp_best.program.to_def("sum_increments", ["lst"]))
