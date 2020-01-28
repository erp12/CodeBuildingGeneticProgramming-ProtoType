from __future__ import annotations

from typing import Iterator, Sequence, Tuple, List, Any, Dict

import numpy as np
from numpy.random import choice
from pyrsistent import v, m, pvector, PVector, PClass, field


class POMap(PClass):
    _keys = field(initial=v())
    _data = field(initial=m())

    @staticmethod
    def from_list(data: Sequence[Tuple]):
        pomap = POMap()
        for key, val in data:
            pomap = pomap.add(key, val)
        return pomap

    @staticmethod
    def from_dict(data: Dict):
        return POMap.from_list(list(data.items()))

    def keys(self) -> PVector:
        return self._keys

    def values(self) -> PVector:
        return pvector([self._data[k] for k in self._keys])

    def items(self) -> List[Tuple[Any, Any]]:
        return [(k, self[k]) for k in self.keys()]

    def add(self, key, value) -> POMap:
        new_data = self._data.set(key, value)
        if key in self._keys:
            ndx = self._keys.index(key)
            new_keys = self._keys.set(ndx, key)
        else:
            new_keys = self._keys.append(key)
        return POMap.create({"_keys": new_keys, "_data": new_data})

    def discard(self, key) -> POMap:
        new_keys = self._keys
        new_data = self._data
        if key in self._keys:
            new_keys = self._keys.remove(key)
            new_data = self._data.discard(key)
        return POMap.create({"_keys": new_keys, "_data": new_data})

    def merge(self, other: POMap) -> POMap:
        new = self
        for key, val in other.items():
            new = new.add(key, val)
        return new

    def __getitem__(self, key):
        if isinstance(key, slice):
            result = [(k, self._data[k]) for k in self._keys[key]]
            return POMap.from_list(result)
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator:
        for k in self._keys:
            yield k, self._data[k]

    def __contains__(self, item):
        return item in self._keys

    def __eq__(self, other):
        return isinstance(other, POMap) and self._keys == other._keys and self._data == other._data


class DiscreteProbDistrib:
    """Discrete Probability Distribution."""

    __slots__ = ["elements", "_total", "_raw_probabilities", "_normalized_probabilities"]

    def __init__(self):
        self.elements = []
        self._total = 0.0
        self._raw_probabilities = []
        self._normalize()

    def _normalize(self):
        self._normalized_probabilities = np.array(self._raw_probabilities) / self._total

    def add(self, el, p):
        """Add an element with a relative probability."""
        self.elements.append(el)
        self._total += float(p)
        self._raw_probabilities.append(p)
        self._normalize()
        return self

    def size(self):
        """Return the number of elements in the distribution."""
        return len(self.elements)

    def sample(self):
        """Return a sample from the distribution."""
        if self.size() == 1:
            return self.elements[0]
        return choice(self.elements, p=self._normalized_probabilities)

    def sample_n(self, n: int = 1, replace: bool = True):
        """Return n samples from the distribution."""
        if self.size() == 1 and replace:
            return [self.elements[0]] * n
        return choice(self.elements, n, replace, self._normalized_probabilities)
