from __future__ import annotations

import random
from typing import Union, List, Tuple

import numpy as np

from push4.gp.evolution import GeneticAlgorithm
from push4.gp.selection import Lexicase
from push4.gp.simplification import GenomeSimplifier
from push4.gp.soup import CoreSoup
from push4.gp.spawn import Spawner
from push4.gp.variation import size_neutral_umad, VariationSet
from push4.lang.dag import Dag

Comparable = Union[int, float, str]


# The target function to evolve.
def target(lst: List[Comparable], lower: Comparable, upper: Comparable) -> List[Comparable]:
    return [el for el in lst if lower <= el <= upper]


def generate_case() -> Tuple[List[Comparable], Comparable, Comparable, List[Comparable]]:
    size = random.randint(0, 10)
    type_name = random.choice(["int", "float", "srt"])
    generator = lambda: random.choice("abcdefghijklmnopqrstuvwxyz")
    if type_name == "int":
        generator = lambda: random.randint(-10, 10)
    elif type_name == "float":
        generator = random.random
    lst = [generator() for _ in range(size)]
    bounds = (generator(), generator())
    lower = min(bounds)
    upper = max(bounds)
    output = target(lst, lower, upper)
    return lst, lower, upper, output


# The penalty error to assign empty programs and programs which produce runtime errors.
penalty = 1e5

X_train = [generate_case() for _ in range(100)]
X_test = [generate_case() for _ in range(100)]


# The error function to guide evolution.
def error(program: Dag) -> np.array:
    errors = []
    for lst, lower, upper, y_true in X_train:
        n_errors = len(y_true) + 1
        if program is None:
            errors += [penalty] * n_errors
        else:
            try:
                y_pred = program.eval(lst=lst, lower=lower, upper=upper)
            except Exception as e:
                # print(e)
                errors += [penalty] * n_errors
                continue
            # Compare the outputs element-wise and compute absolute errors.
            for ndx, el_pred in enumerate(y_pred[:len(y_true)]):
                el_true = y_true[ndx]
                errors.append(int(el_true != el_pred))
            # If y_pred is shorter than y_true, fill in missing elements with penalties.
            for _ in range(max(0, len(y_true) - len(y_pred))):
                errors.append(penalty)
            # Add the difference in size as an error.
            errors.append(abs(len(y_true) - len(y_pred)))
    return np.array(errors)


# The "soup" containing all expression which might appear in evolved programs.
soup = (
    CoreSoup()
        .register_input("lst", List[Comparable])
        .register_input("lower", Comparable)
        .register_input("upper", Comparable)
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

OUTPUT_TYPE = List[Comparable]

simplifier = GenomeSimplifier(error, OUTPUT_TYPE)

if __name__ == "__main__":
    best = evo.run(OUTPUT_TYPE)
    print(best.program.to_def("filter_bounds", ["lst", "lower", "upper"]))
    simp_best = simplifier.simplify(best)
    print(simp_best.program.to_def("filter_bounds", ["lst", "lower", "upper"]))

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
