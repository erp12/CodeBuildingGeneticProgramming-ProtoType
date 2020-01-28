import operator
from abc import ABC, abstractmethod
from typing import Mapping, Sequence, Set, List

from pyrsistent import PRecord, field, pmap_field
from pytypes import get_Generic_itemtype

from push4.collections import POMap


class Signature(PRecord):
    ret = field()
    args = field(POMap)


class TypeReifier(ABC):

    @abstractmethod
    def reify(self, signature: Signature, children: Mapping[str, type]) -> Signature:
        ...


class ReifierChain(TypeReifier):

    def __init__(self, reifiers: Sequence[TypeReifier]):
        self.reifiers = reifiers

    def reify(self, signature: Signature, children: Mapping[str, type]) -> Signature:
        new_sig = signature
        for r in self.reifiers:
            new_sig = r.reify(new_sig, children)
        return new_sig


class NoopReifier(TypeReifier):

    def reify(self, signature: Signature, children: Mapping[str, type]) -> Signature:
        return signature


class RequiredReifier(TypeReifier):

    def reify(self, signature: Signature, children: Mapping[str, type]) -> Signature:
        new_sig = signature
        for nm, typ in children.items():
            new_sig = new_sig.set("args", new_sig.args.add(nm, typ))
        return new_sig


class PassThroughReifier(TypeReifier):

    def __init__(self, arg_name: str):
        self.arg_name = arg_name

    def reify(self, signature: Signature, children: Mapping[str, type]) -> Signature:
        if self.arg_name in children:
            return signature.set(ret=children[self.arg_name])
        return signature


class MaxTypeReifier(TypeReifier):

    def __init__(self, type_seq: Sequence[type]):
        self.type_seq = type_seq

    def reify(self, signature: Signature, children: Mapping[str, type]) -> Signature:
        try:
            ndxs = {nm: self.type_seq.index(t) for nm, t in children.items()}
            arg_name = max(ndxs.items(), key=operator.itemgetter(1))[0]
            return signature.set(ret=children[arg_name])
        except ValueError as e:
            return signature


class RetToElementType(TypeReifier):

    def __init__(self, collection_arg_name: str):
        self.collection_arg_name = collection_arg_name

    def reify(self, signature: Signature, children: Mapping[str, type]) -> Signature:
        if self.collection_arg_name in children:
            coll_type = children[self.collection_arg_name]
            return signature.set(ret=get_Generic_itemtype(coll_type))
        return signature


class ArgsToElementType(TypeReifier):

    def __init__(self, coll_arg_name: str, elem_arg_names: Set[str]):
        self.coll_arg_name = coll_arg_name
        self.elem_arg_names = elem_arg_names

    def reify(self, signature: Signature, children: Mapping[str, type]) -> Signature:
        if self.coll_arg_name in children:
            typ = get_Generic_itemtype(children[self.coll_arg_name])
            new_args = signature.args
            for el in self.elem_arg_names:
                new_args = new_args.add(el, typ)
            return signature.set(args=new_args)
        return signature


class ArgsToSame(TypeReifier):

    def __init__(self, ref_arg: str, other_args: Set[str]):
        self.ref_arg = ref_arg
        self.other_args = other_args

    def reify(self, signature: Signature, children: Mapping[str, type]) -> Signature:
        if self.ref_arg in children:
            typ = children[self.ref_arg]
            new_args = signature.args.add(self.ref_arg, typ)
            for a in self.other_args:
                new_args = new_args.add(a, typ)
            return signature.set(args=new_args)
        return signature


class ListOf(TypeReifier):

    def __init__(self, el_arg: str):
        self.el_arg = el_arg

    def reify(self, signature: Signature, children: Mapping[str, type]) -> Signature:
        if self.el_arg in children:
            return signature.set(ret=List[children[self.el_arg]])
        return signature
