import pytest
from pyrsistent import v, m

from push4.collections import POMap


class TestPOMap:

    def test_create(self):
        a = POMap()
        assert a.keys() == v()
        assert a.values() == v()

        b = a.add("A", 1).add(2, ["x", "y", "z"]).add("A", 100)
        assert b.keys() == v("A", 2)
        assert b.values() == v(100, ["x", "y", "z"])

        c = POMap.from_list([("A", 1), ("B", 2), ("A", 100)])
        assert c.keys() == v("A", "B")
        assert c.values() == v(100, 2)

    def test_add_discard(self):
        a = POMap().add("A", 100).discard("A")
        assert a.keys() == v()
        assert a.values() == v()

    def test_merge(self):
        a = POMap().add("A", 1).add("B", 2)
        b = POMap().add("C", 3).add("A", 100)
        c = a.merge(b)
        assert c.keys() == v("A", "B", "C")
        assert c.values() == v(100, 2, 3)

    def test_iter_and_slice(self):
        a = POMap()
        letters = "abcdefghij"
        for ndx in range(10):
            a = a.add(letters[ndx], ndx)
        a = a[-3:]
        assert a.keys() == v("h", "i", "j")
        assert a.values() == v(7, 8, 9)

    def test_keep_order(self):
        po_map = POMap()
        po_map = po_map.add("a", 1)
        assert po_map.keys() == v("a")
        po_map = po_map.add("b", 2)
        assert po_map.keys() == v("a", "b")
        po_map = po_map.add("a", 3)
        assert po_map.keys() == v("a", "b")
        assert po_map.values() == v(3, 2)
