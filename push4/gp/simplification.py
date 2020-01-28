from copy import copy
from typing import Callable, Sequence, Tuple

import numpy as np
from pyrsistent import pvector

from push4.gp.spawn import genome_to_push_code
from push4.lang.dag import Dag
from push4.lang.expr import Expression
from push4.gp.individual import Genome, Individual
from push4.lang.push import Push


class GenomeSimplifier:
    """Simplifies a genome while preserving, or improving, its error.
    Genomes, and Push programs, can contain superfluous Push code. This extra
    code often has no effect on the program behavior, but occasionally it can
    introduce subtle errors or behaviors that is not covered by the training
    cases. Removing the superfluous code makes genomes (and thus programs)
    smaller and easier to understand. More importantly, simplification can
    improve the generalization of the given genome/program.
    The process of genome simplification is iterative and closely resembles
    simple hill climbing. For each iteration, the simplifier will randomly
    select a small number of random genes to remove. The Genome is re-evaluated
    and if its error gets worse, the change is reverted. After repeating this
    for some number of steps, the resulting genome will be the same size or
    smaller while containing the same (or better) error value.

    Reference:
    "Improving generalization of evolved programs through automatic simplification"
    Thomas Helmuth, Nicholas Freitag McPhee, Edward Pantridge, and Lee Spector. 2017.
    In Proceedings of the Genetic and Evolutionary Computation Conference (GECCO '17).
    ACM, New York, NY, USA, 937-944. DOI: https://doi.org/10.1145/3071178.3071330
    https://dl.acm.org/citation.cfm?id=3071178.3071330
    """

    # @TODO: Add noop swaps to simplification.

    def __init__(self,
                 error_fn: Callable[[Dag], np.array],
                 output_type: type):
        self.error_fn = error_fn
        self.output_type = output_type

    def _remove_rand_genes(self, genome: Genome) -> Genome:
        gn = pvector(genome)
        n_genes_to_remove = min(np.random.randint(1, len(gn) // 2), len(gn) - 1)
        ndx_of_genes_to_remove = np.random.choice(np.arange(len(gn)), n_genes_to_remove, replace=False)
        ndx_of_genes_to_remove[::-1].sort()
        for ndx in ndx_of_genes_to_remove:
            gn = gn.delete(ndx)
        return gn

    def _errors_of_genome(self, genome: Genome) -> np.ndarray:
        push_code = genome_to_push_code(genome)
        dag = Push().compile(push_code, self.output_type)
        return self.error_fn(dag)

    def _step(self, genome: Genome, errors_to_beat: np.ndarray) -> Tuple[Genome, np.ndarray]:
        new_gn = self._remove_rand_genes(genome)
        new_errs = self._errors_of_genome(new_gn)
        if np.sum(new_errs) <= np.sum(errors_to_beat):
            print("Simplified to length {ln}.".format(ln=len(new_gn)))
            return new_gn, new_errs
        return genome, errors_to_beat

    def simplify(self,
                 individual: Individual,
                 steps: int = 2000) -> Individual:
        """Simplify the given genome while maintaining error.
        Parameters
        ----------
        individual: Individual
            Individual to simplify.
        steps
            Number of simplification iterations to perform. Default is 2000.
        Returns
        -------
        pushgp.gp.genome.Genome
            A Genome with random contents of a given size.
        """
        gn = individual.genome
        errs = individual.error_vector
        print("Simplifying genome of length {ln}.".format(ln=len(gn)))
        for step in range(steps):
            gn, errs = self._step(gn, errs)
            if len(gn) == 1:
                break
        print("Simplified genome: length={ln} error={te}".format(ln=len(gn), te=np.sum(errs)))
        simplified_individual = Individual(gn, individual.output_type)
        simplified_individual.error_vector = errs
        return simplified_individual


# @TODO: DAG simplification
#   1. If all leaves are constant, replace subtree with constant.
#   2. Replace `t + 0` with t.
#   3. Replace `t * 0` with 0.

