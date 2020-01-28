from __future__ import annotations

import numpy as np

from push4.lang.expr import Function, Input
from push4.library import op
from push4.gp.evolution import GeneticAlgorithm
from push4.gp.selection import Lexicase
from push4.gp.simplification import GenomeSimplifier
from push4.gp.soup import Soup, CoreSoup
from push4.gp.spawn import Spawner
from push4.gp.variation import umad, size_neutral_umad, VariationSet, Alternation, Genesis
from push4.lang.dag import Dag


# The target function to evolve.
def target(i: int, dec: bool) -> int:
    return i - 1 if dec else i + 1


x_train = list(zip(
    range(-10, 10),
    [True, False] * 10
))

# The penalty error to assign empty programs and programs which produce runtime errors.
penalty = 1e5


# The error function to guide evolution.
def error(program: Dag) -> np.array:
    errors = []
    for i, dec in x_train:
        if program is None:
            errors.append(penalty)
        else:
            y_true = target(i, dec)
            try:
                y_pred = program.eval(i=i, dec=dec)
                errors.append(abs(y_true - y_pred))
            except Exception as e:
                # print(e)
                errors.append(penalty)
    return np.array(errors)


# The "soup" containing all expression which might appear in evolved programs.
soup = (
    CoreSoup()
    .register_input("i", int)
    .register_input("dec", bool)
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


simplifier = GenomeSimplifier(error, int)


if __name__ == "__main__":
    best = evo.run(int)
    print(best.program.to_def("inc_or_dec", ["i", "dec"]))
    simp_best = simplifier.simplify(best)
    print(simp_best.program.to_def("inc_or_dec", ["i", "dec"]))
