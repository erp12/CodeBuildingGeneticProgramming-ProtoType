from typing import Dict, List, Any, Sequence

from push4.collections import POMap
from push4.lang.reify import PassThroughReifier, Signature, RequiredReifier, MaxTypeReifier, ArgsToElementType, \
    ArgsToSame, ReifierChain
from push4.library.op import Numeric


class TestRequiredReifier:

    def test_reify_with_new_child(self):
        reifier = RequiredReifier()
        sig = Signature(ret=Dict, args=POMap().add("a", Dict).add("b", Any))
        actual = reifier.reify(sig, {"a": Dict[str, List[int]]})
        expected = Signature(ret=sig.ret, args=sig.args.add("a", Dict[str, List[int]]))
        assert actual == expected

    def test_reify_with_new_children(self):
        reifier = RequiredReifier()
        sig = Signature(ret=Dict, args=POMap().add("a", Dict).add("b", Any))
        actual = reifier.reify(sig, {"a": Dict[str, List[int]], "b": float})
        expected = Signature(ret=sig.ret,
                             args=POMap().add("a", Dict[str, List[int]]).add("b", float))
        assert actual == expected


class TestPassThroughReifier:

    def test_reify(self):
        reifier = PassThroughReifier("a")
        sig = Signature(ret=Dict, args=POMap().add("a", Dict).add("b", Any))
        actual = reifier.reify(sig, {"a": Dict[str, List[int]], "b": float})
        expected = Signature(ret=Dict[str, List[int]], args=sig.args)
        assert actual == expected


class TestMaxTypeReifier:

    def test_reify_to_min(self):
        reifier = MaxTypeReifier([int, float])
        sig = Signature(ret=Numeric, args=POMap().add("a", Numeric).add("b", Numeric))
        actual = reifier.reify(sig, {"a": int, "b": int})
        expected = sig.set("ret", int)
        assert actual == expected

    def test_reify_to_max(self):
        reifier = MaxTypeReifier([int, float])
        sig = Signature(ret=Numeric, args=POMap().add("a", Numeric).add("b", Numeric))
        actual = reifier.reify(sig, {"a": int, "b": float})
        expected = sig.set("ret", float)
        assert actual == expected


class TestArgsToElementType:

    def test_reify(self):
        reifier = ArgsToElementType("coll", {"obj"})
        sig = Signature(ret=bool, args=POMap().add("coll", Sequence).add("obj", Any))
        actual = reifier.reify(sig, {"coll": Sequence[str]})
        expected = sig.set("args", sig.args.add("obj", str))
        assert actual == expected


class TestArgsToSame:

    def test_reify(self):
        reifier = ArgsToSame("a", {"b", "c"})
        sig = Signature(ret=bool, args=POMap().add("coll", List).add("a", Any).add("b", Any).add("c", Any))
        actual = reifier.reify(sig, {"a": int})
        expected = Signature(ret=bool, args=POMap().add("coll", List).add("a", int).add("b", int).add("c", int))
        assert actual == expected


class TestReifierChain:

    def test_reify(self):
        reifier = ReifierChain([
            ArgsToSame("a", {"b"}),
            PassThroughReifier("a")
        ])
        sig = Signature(ret=Any, args=POMap().add("a", Any).add("b", Any))
        actual = reifier.reify(sig, {"a": int})
        expected = Signature(ret=int, args=POMap().add("a", int).add("b", int))
        assert actual == expected
