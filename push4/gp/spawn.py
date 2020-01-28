import random
from copy import deepcopy
from typing import Sequence, Union

from pyrsistent import pvector, PVector

from push4.gp.soup import Soup, Unit, GeneToken, ErcGenerator
from push4.lang.expr import Expression


def genome_to_push_code(genome: Sequence[Unit]) -> Sequence[Union[Expression, PVector]]:
    buffer = pvector(genome)
    push_code = []
    while True:
        # If done with plush but unclosed opens, recur with one more close.
        if len(buffer) == 0 and GeneToken.OPEN in push_code:
            buffer = buffer.append(GeneToken.CLOSE)
        # If done with plush and all opens closed, return push.
        elif len(buffer) == 0:
            return pvector(push_code)
        else:
            gene = buffer[0]
            # If next instruction is a close, and there is an open.
            if gene == GeneToken.CLOSE and GeneToken.OPEN in push_code:
                ndx, opener = [(ndx, el) for ndx, el in enumerate(push_code) if el == GeneToken.OPEN][-1]
                post_open = push_code[ndx + 1:]
                pre_open = push_code[:ndx]
                push_code = pre_open + [pvector(post_open)]
            # If next instruction is a close, and there is no open.
            elif not gene == GeneToken.CLOSE:
                push_code.append(gene)
            buffer = buffer.delete(0)


class Spawner:

    def __init__(self, soup: Soup):
        self.soup = soup

    def spawn_gene(self) -> Expression:
        return deepcopy(self.soup.random_unit())

    def spawn_genome_of_size(self, size: int) -> Sequence[Unit]:
        return pvector([self.spawn_gene() for _ in range(size)])

    def spawn_genome(self, min_size: int, max_size: int) -> Sequence[Unit]:
        size = random.randint(min_size, max_size)
        return self.spawn_genome_of_size(size)

    def spawn_push_code_of_size(self, size: int) -> Sequence[Expression]:
        return genome_to_push_code(self.spawn_genome_of_size(size))

    def spawn_push_code(self, min_size: int, max_size: int) -> Sequence[Expression]:
        return genome_to_push_code(self.spawn_genome(min_size, max_size))
