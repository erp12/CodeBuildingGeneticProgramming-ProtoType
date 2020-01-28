from __future__ import annotations

import numpy as np

from push4.gp.evolution import GeneticAlgorithm
from push4.gp.selection import Lexicase
from push4.gp.simplification import GenomeSimplifier
from push4.gp.soup import CoreSoup
from push4.gp.spawn import Spawner
from push4.gp.variation import size_neutral_umad, VariationSet
from push4.lang.dag import Dag


# The target function to evolve.
from push4.lang.expr import Expression, Constant, Input


def target(x1: float, x2: float) -> float:
    return (x1 ** 2) + x2 + 3


x_train = np.random.random((100, 2)) * 100 - 50

# The penalty error to assign empty programs and programs which produce runtime errors.
penalty = 1e6


# The error function to guide evolution.
def error(program: Dag) -> np.array:
    errors = []
    for x1, x2 in x_train:
        if program is None:
            errors.append(penalty)
            errors.append(penalty)
        else:
            y_true = target(x1, x2)
            try:
                y_pred = program.eval(x1=float(x1), x2=float(x2))
                errors.append(float(not isinstance(y_pred, float)))
                errors.append(float((y_true - y_pred) ** 2))
            except Exception as e:
                # print(e)
                errors.append(penalty)
                errors.append(penalty)
    return np.array(errors)


# The "soup" containing all expression which might appear in evolved programs.
soup = (
    CoreSoup()
    .register_constants([x for x in range(10)])
    .register_input("x1", float)
    .register_input("x2", float)
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
    initial_genome_size=(10, 60)
)

simplifier = GenomeSimplifier(error, bool)

if __name__ == "__main__":
    best = evo.run(float)
    print(best.program.to_def("f", ["x1", "x2"]))
    simp_best = simplifier.simplify(best)
    print(simp_best.program.to_def("f", ["x1", "x2"]))
    print(simp_best.program.eval(x1=2.0, x2=3.0))
