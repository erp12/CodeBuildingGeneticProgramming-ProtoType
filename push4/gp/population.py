from collections.abc import Sequence
from bisect import insort_left
from typing import Callable

import numpy as np
import pickle
from multiprocessing import Pool
from functools import partial

from push4.gp.individual import Individual
from push4.lang.dag import Dag


def _eval_indiv(indiv: Individual, error_fn: Callable[[Dag], np.array]):
    indiv.error_vector = error_fn(indiv.program)
    return indiv


class Population(Sequence):
    """A sequence of Individuals kept in sorted order, with respect to their total errors."""

    __slots__ = ["unevaluated", "evaluated"]

    def __init__(self, individuals: list = None):
        self.unevaluated = []
        self.evaluated = []

        if individuals is not None:
            for el in individuals:
                self.add(el)

    def __len__(self):
        return len(self.evaluated) + len(self.unevaluated)

    def __getitem__(self, key: int) -> Individual:
        if key < len(self.evaluated):
            return self.evaluated[key]
        return self.unevaluated[key - len(self.evaluated)]

    def add(self, individual: Individual):
        """Add an Individual to the population."""
        if individual.total_error is None:
            self.unevaluated.append(individual)
        else:
            insort_left(self.evaluated, individual)
        return self

    def best(self):
        """Return the best n individual in the population."""
        return self.evaluated[0]

    def best_n(self, n: int):
        """Return the best n individuals in the population."""
        return self.evaluated[:n]

    def p_evaluate(self, error_fn, pool: Pool):
        """Evaluate all unevaluated individuals in the population in parallel."""
        func = partial(_eval_indiv, error_fn=error_fn)
        for individual in pool.imap_unordered(func, self.unevaluated):
            insort_left(self.evaluated, individual)
        self.unevaluated = []

    def evaluate(self, error_fn: Callable[[Dag], np.array]):
        """Evaluate all unevaluated individuals in the population."""
        for individual in self.unevaluated:
            individual = _eval_indiv(individual, error_fn)
            insort_left(self.evaluated, individual)
        self.unevaluated = []

    def all_error_vectors(self):
        """2D array containing all Individuals' error vectors."""
        return np.vstack([i.error_vector for i in self.evaluated])

    def all_total_errors(self):
        """1D array containing all Individuals' total errors."""
        return np.array([i.total_error for i in self.evaluated])

    def median_error(self):
        """Median total error in the population."""
        return np.median(self.all_total_errors())

    def error_diversity(self):
        """Proportion of unique error vectors."""
        return len(np.unique(self.all_error_vectors(), axis=0)) / float(len(self))

    def genome_diversity(self):
        """Proportion of unique genomes."""
        unq = set([pickle.dumps(i.genome) for i in self])
        return len(unq) / float(len(self))

    def program_diversity(self):
        """Proportion of unique programs."""
        unq = set([pickle.dumps(i.get_program().code) for i in self])
        return len(unq) / float(len(self))
