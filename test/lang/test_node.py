import pytest

from push4.collections import POMap
from push4.lang.node import Node


@pytest.fixture
def empty_node() -> Node:
    return Node()


@pytest.fixture
def simple_tree() -> Node:
    root = Node()
    root.add_children({
        "l": Node(),
        "r": Node()
    })
    root.children["r"].add_child("a", Node())
    return root


class TestNode:

    def test_flush_children(self, empty_node: Node, simple_tree: Node):
        empty_node.flush_children()
        assert empty_node.children == POMap()
        assert empty_node.depth == 1

        simple_tree.flush_children()
        assert simple_tree.children == POMap()
        assert simple_tree.depth == 1

    def test_add_children(self, empty_node: Node, simple_tree: Node):
        empty_node.add_child("c", Node())
        assert empty_node.children == POMap().from_dict({"c": Node()})

        new_children = {
            "c": Node().add_child("c2", Node()),
            "c3": Node()
        }
        empty_node.add_children(new_children)
        assert empty_node.children == POMap().from_dict(new_children)

        simple_tree.add_child("c", Node())
        assert simple_tree.children == POMap().from_dict({
            "l": Node(),
            "r": Node().add_child("a", Node()),
            "c": Node()
        })

    def test_reify(self, empty_node: Node, simple_tree: Node):
        empty_node.reify()
        assert empty_node.reified

        simple_tree.reify()
        for child in simple_tree.children.values():
            assert child.reified
        assert simple_tree.reified

    def test_pprint(self, empty_node: Node, simple_tree: Node, capsys):
        empty_node.pprint()
        captured = capsys.readouterr()
        assert captured.out == "- Node<children=0,depth=1>\n"

        simple_tree.pprint()
        captured = capsys.readouterr()
        assert captured.out == ("- Node<children=2,depth=2>\n"
                                "| - Node<children=0,depth=1>\n"
                                "| - Node<children=1,depth=2>\n"
                                "| | - Node<children=0,depth=1>\n")
