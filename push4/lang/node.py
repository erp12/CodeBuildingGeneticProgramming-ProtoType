from __future__ import annotations

from typing import Mapping

from pyrsistent import m, v

from push4.collections import POMap


class Node:

    def __init__(self):
        self.children = POMap()
        self.reified = False
        self.depth = 1

    def flush_children(self):
        self.children = POMap()
        self._update_depth()
        return self

    def add_children(self, children: Mapping[str, Node]):
        self.children = self.children.merge(children)
        self._update_depth()
        return self

    def add_child(self, name: str, child: Node):
        self.children = self.children.add(name, child)
        self._update_depth()
        return self

    def _reify(self):
        pass

    def reify(self, include_children: bool = False):
        if include_children:
            for _, child in self.children.items():
                child.reify()
        self._reify()
        self.reified = True

    def pprint(self, depth: int = 0):
        print("| " * depth + "- " + str(self))
        for child in self.children.values():
            child.pprint(depth + 1)

    def _update_depth(self):
        self.depth = max([0] + [child.depth for child in self.children.values()]) + 1

    def __repr__(self):
        return "Node<children={c},depth={d}>".format(
            c=len(self.children),
            d=self.depth
        )

    def __eq__(self, other: Node):
        if not isinstance(other, Node):
            return False
        return self.reified == other.reified and self.children == other.children
