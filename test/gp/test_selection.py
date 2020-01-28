from typing import Any

import numpy as np

from push4.gp.individual import Individual
from push4.gp.population import Population
from push4.gp.selection import CaseStream, Lexicase, one_individual_per_error_vector


class MockIndividual(Individual):

    def __init__(self, name, error_vec):
        super().__init__([], Any)
        self.name = name
        self.error_vector = np.array(error_vec)


class MockCaseStream(CaseStream):

    def __iter__(self):
        # Disables case shuffling for testing.
        for case in self.cases:
            yield case


class TestLexicase:

    def test_lexicase(self):
        pop = Population([
            MockIndividual("A", [0, 0, 1]),
            MockIndividual("B", [0, 1, 0]),
            MockIndividual("C", [1, 0, 0]),
        ])
        lexicase = Lexicase()
        cases = MockCaseStream(3)
        selected = lexicase._select_with_stream(pop, cases)
        assert selected.name == "A"

    def test_lexicase_tie(self):
        pop = Population([
            MockIndividual("A", [0, 0, 0]),
            MockIndividual("B", [1, 1, 1]),
            MockIndividual("C", [0, 0, 0]),
        ])
        for _ in range(10):
            preselected = one_individual_per_error_vector(pop)
            assert len(preselected) == 2
            pre_sel_names = set([i.name for i in preselected])
            assert pre_sel_names == {"A", "B"} or pre_sel_names == {"B", "C"}

            lexicase = Lexicase()
            cases = MockCaseStream(3)
            selected = lexicase._select_with_stream(pop, cases)
            assert selected.name in ("A", "C")

    def test_epsilon_lexicase_scalar(self):
        pop = Population([
            MockIndividual("A", [0.1, 0.1, 0.1]),
            MockIndividual("B", [0.2, 0.2, 1.0]),
            MockIndividual("C", [0.3, 1.0, 1.0]),
        ])
        for _ in range(10):
            lexicase = Lexicase(epsilon=0.1)
            cases = MockCaseStream(3)
            selected = lexicase._select_with_stream(pop, cases)
            assert selected.name == "A"

    def test_epsilon_lexicase_array(self):
        pop = Population([
            MockIndividual("A", [0.1, 0.1, 0.1]),
            MockIndividual("B", [0.2, 0.2, 0.11]),
            MockIndividual("C", [0.3, 0.3, 1.0]),
        ])
        for _ in range(10):
            print(_)
            lexicase = Lexicase(epsilon=np.array([0.2, 0.1, 0.0]))
            cases = MockCaseStream(3)
            selected = lexicase._select_with_stream(pop, cases)
            assert selected.name == "A"

    def test_epsilon_lexicase_mad(self):
        pop = Population([
            MockIndividual("A", [1,  3, 10]),
            MockIndividual("B", [2,  1, 100]),
            MockIndividual("C", [3, 10, 2]),
        ])
        for _ in range(10):
            lexicase = Lexicase(epsilon=True)

            epsilon_vec = lexicase._epsilon_from_mad(pop.all_error_vectors())
            assert list(epsilon_vec) == [1, 2, 8]

            cases = MockCaseStream(3)
            selected = lexicase._select_with_stream(pop, cases)
            assert selected.name == "A"
