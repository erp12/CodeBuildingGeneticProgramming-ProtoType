from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Union, List, Tuple

import numpy as np

from push4.gp.evolution import GeneticAlgorithm
from push4.gp.selection import Lexicase
from push4.gp.simplification import GenomeSimplifier
from push4.gp.soup import CoreSoup
from push4.gp.spawn import Spawner
from push4.gp.variation import size_neutral_umad, VariationSet
from push4.lang.dag import Dag


class DateTime:

    def year(self: datetime) -> int:
        return self.year

    def month(self: datetime) -> int:
        return self.month

    def day(self: datetime) -> int:
        return self.day

    def hour(self: datetime) -> int:
        return self.hour

    def minute(self: datetime) -> int:
        return self.minute

    def second(self: datetime) -> int:
        return self.second


class TimeDelta:

    def days(self: timedelta) -> int:
        return self.days

    def seconds(self: timedelta) -> int:
        return self.seconds


def sub(a: datetime, b: datetime) -> timedelta:
    return a - b


# The target function to evolve.
def target(dt1: datetime, dt2: datetime) -> int:
    return abs((dt1 - dt2).days)


def random_datetime() -> datetime:
    return datetime(
        year=random.randint(1990, 2020),
        month=random.randint(1, 12),
        day=random.randint(1, 28),
        hour=random.randint(0, 23),
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
    )


def generate_case() -> Tuple[datetime, datetime, int]:
    a = random_datetime()
    b = random_datetime()
    y_true = target(a, b)
    return a, b, y_true


# The penalty error to assign empty programs and programs which produce runtime errors.
penalty = 1e5

X_train = [generate_case() for _ in range(100)]
X_test = [generate_case() for _ in range(100)]


# The error function to guide evolution.
def error(program: Dag) -> np.array:
    errors = []
    for dt1, dt2, y_true in X_train:
        if program is None:
            errors.append(penalty)
        else:
            try:
                y_pred = program.eval(dt1=dt1, dt2=dt2)
                errors.append(abs(y_pred - y_true))
            except Exception as e:
                # print(e)
                errors.append(penalty)
                continue
    return np.array(errors)


# The "soup" containing all expression which might appear in evolved programs.
soup = (
    CoreSoup()
    .register_methods(DateTime)
    .register_methods(TimeDelta)
    .register_function(sub)
    .register_constant(365)
    .register_input("dt1", datetime)
    .register_input("dt2", datetime)
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

OUTPUT_TYPE = int

simplifier = GenomeSimplifier(error, OUTPUT_TYPE)

if __name__ == "__main__":
    best = evo.run(OUTPUT_TYPE)
    print(best.program.to_def("days_between", ["dt1", "dt1"]))
    simp_best = simplifier.simplify(best)
    print(simp_best.program.to_def("days_between", ["dt1", "dt2"]))

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
