from __future__ import annotations

import random
from typing import Union, List, Tuple

import os.path as path
import numpy as np

from push4.gp.evolution import GeneticAlgorithm
from push4.gp.selection import Lexicase
from push4.gp.simplification import GenomeSimplifier
from push4.gp.soup import CoreSoup
from push4.gp.spawn import Spawner
from push4.gp.variation import size_neutral_umad, VariationSet
from push4.lang.dag import Dag
from push4.utils import damerau_levenshtein_distance


class SimplePath:

    def __init__(self, path_str: str):
        self.path_str = path_str

    def to_str(self: SimplePath) -> str:
        return self.path_str

    def abspath(self: SimplePath) -> SimplePath:
        return SimplePath(path.abspath(self.path_str))

    def split(self: SimplePath) -> List[str]:
        return list(path.split(self.path_str))

    def basename(self: SimplePath) -> str:
        return path.basename(self.path_str)

    def dirname(self: SimplePath) -> SimplePath:
        return SimplePath(path.dirname(self.path_str))

    def isabs(self: SimplePath) -> bool:
        return path.isabs(self.path_str)

    def join(self: SimplePath, other: SimplePath) -> SimplePath:
        return SimplePath(path.join(self.path_str, other.path_str))


# The target function to evolve.
def target(root: SimplePath, filenames: List[str]) -> List[SimplePath]:
    return [root.join(SimplePath(fn)) for fn in filenames]


def random_str():
    size = random.randint(1, 10)
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=size))


def random_path():
    path_str = ""
    if random.randint(0, 1) == 1:
        path_str += "/"
    for _ in range(random.randint(0, 3)):
        path_str += random_str() + "/"
    if random.randint(0, 1) == 1:
        path_str = path_str[:-1]
    return SimplePath(path_str)


def random_case():
    root = random_path()
    num_files = random.randint(0, 5)
    filenames = [random_str() for _ in range(num_files)]
    return root, filenames


x_train = [
    (SimplePath("/"), ["a", "b", "c"]),
    (SimplePath("a"), ["bbb", "ccc"]),
    (SimplePath("a/b"), ["c"]),
    (SimplePath("/a/b/c"), []),
    (SimplePath("/a/b/c"), ["d", "e", "f"]),
    (SimplePath(""), ["abc", "def", "ghi"]),
    (SimplePath("some/root/path"), ["a", "bb", "ccc", "dddd", "eeeee"])
] + [random_case() for _ in range(100)]
y_train = [target(root, filenames) for root, filenames in x_train]


# The penalty error to assign empty programs and programs which produce runtime errors.
penalty = 1e5


# The error function to guide evolution.
def error(program: Dag) -> np.array:
    errors = []
    for ndx, (root, filenames) in enumerate(x_train):
        y_true = y_train[ndx]
        n_errors = len(y_true) + 1
        if program is None:
            errors += [penalty] * n_errors
        else:
            try:
                y_pred = program.eval(root=root, filenames=filenames)
            except Exception as e:
                # print(e)
                errors += [penalty] * n_errors
                continue
            # Compare the outputs element-wise and compute absolute errors.
            for ndx, el_pred in enumerate(y_pred[:len(y_true)]):
                el_true = y_true[ndx]
                errors.append(damerau_levenshtein_distance(el_true.path_str, el_pred.path_str))
            # If y_pred is shorter than y_true, fill in missing elements with penalties.
            for _ in range(max(0, len(y_true) - len(y_pred))):
                errors.append(penalty)
            # Add the difference in size as an error.
            errors.append(abs(len(y_true) - len(y_pred)))
    return np.array(errors)


# The "soup" containing all expression which might appear in evolved programs.
soup = (
    CoreSoup()
    .register_class(SimplePath)
    .register_input("root", SimplePath)
    .register_input("filenames", List[str])
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

OUTPUT_TYPE = List[SimplePath]

simplifier = GenomeSimplifier(error, OUTPUT_TYPE)

if __name__ == "__main__":
    best = evo.run(OUTPUT_TYPE)
    print(best.program.to_def("prefix_files", ["root", "filenames"]))
    simp_best = simplifier.simplify(best)
    print(simp_best.program.to_def("prefix_files", ["root", "filenames"]))

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
