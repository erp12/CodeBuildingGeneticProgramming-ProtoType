from typing import Any, Sized, Iterable, List, Dict, MutableSet, Union, Tuple, Mapping

from push4.lang.reify import ReifierChain, ArgsToElementType, PassThroughReifier, RetToElementType, ArgsToSame, ListOf


def len_(coll: Sized) -> int:
    return len(coll)


def in_(coll: Union[List, Dict, MutableSet], el: Any) -> bool:
    return el in coll


def add(l1: List, l2: List) -> List:
    return l1 + l2


def wrap(el: Any) -> List:
    return [el]


_add_reifier = ReifierChain([
    ArgsToSame("l1", {"l2"}),
    PassThroughReifier("l1")
])


fns = [
    (len_, None),
    (in_, ArgsToElementType("coll", {"el"})),
    (add, _add_reifier),
    (wrap, ListOf("el"))
]


# class List_(list):
#
#     def remove(self: list, object: Any) -> list:
#         list.remove(self, object)
#         return self
#
#     def append(self: list, object: Any) -> list:
#         list.append(self, object)
#         return self
#
#     def del_(self: list, ndx: int) -> list:
#         del self[ndx]
#         return self
#
#     def index(self: list, object: Any) -> int:
#         return list.index(self, object)
#
#     def count(self: list, object: Any) -> int:
#         return list.count(self, object)
#
#     def pop(self: list, index: int = 0) -> Any:
#         return list.pop(self, index)
#
#     def pop_top(self: list) -> Any:
#         return self.pop()
#
#     def clear(self: list) -> list:
#         list.clear(self)
#         return self
#
#     def extend(self: list, iterable: Iterable[Any]) -> list:
#         list.extend(self, iterable)
#         return self
#
#     def insert(self: list, index: int, object: Any) -> list:
#         list.insert(self, index, object)
#         return self
#
#     def reverse(self: list) -> list:
#         list.reverse(self)
#         return self
#
#     def sort(self: list, reverse: bool = False) -> None:
#         list.sort(reverse=reverse)
#         return self
#
#     def sort_acs(self: list):
#         return self.sort()
#
#     def sort_desc(self: list):
#         return self.sort(reverse=True)
#
#     def get(self: list, ndx: int) -> Any:
#         return self[ndx]
#
#     def set(self: list, ndx: int, obj: Any) -> list:
#         self[ndx] = obj
#         return self
#
#
# _ret_to_element = RetToElementType("self")
# _object_to_element = ArgsToElementType("self", {"object"})
# _pass_self = PassThroughReifier("self")
#
#
# List_reifiers = {
#     "remove": ReifierChain([
#         _object_to_element,
#         _pass_self,
#     ]),
#     "append": ReifierChain([
#         _object_to_element,
#         _pass_self,
#     ]),
#     "del_": _pass_self,
#     "index": _object_to_element,
#     "count": _object_to_element,
#     "pop": _ret_to_element,
#     "pop_top": _ret_to_element,
#     "clear": _pass_self,
#     "extend": ReifierChain([
#         ArgsToSame("self", {"iterable"}),
#         _pass_self,
#     ]),
#     "insert": ReifierChain([
#         _object_to_element,
#         _pass_self,
#     ]),
#     "reverse": _pass_self,
#     "sort": _pass_self,
#     "sort_acs": _pass_self,
#     "sort_desc": _pass_self,
#     "get": _ret_to_element,
#     "set": ReifierChain([
#         _object_to_element,
#         _pass_self
#     ]),
# }


# class Dict(dict):
#
#     def clear(self: dict) -> dict:
#         dict.clear(self)
#         return self
#
#     def get(self: dict, k: Any) -> Any:
#         return self[k]
#
#     def set(self: dict, k: Any, v: Any) -> dict:
#         self[k] = v
#         return self
#
#     def items(self: dict) -> List[Tuple[Any, Any]]:
#         return list(dict.items(self))
#
#     def keys(self: dict) -> List[Any]:
#         return list(dict.keys(self))
#
#     def pop(self: dict, k: Any) -> Any:
#         v = self[k]
#         del self[k]
#         return v
#
#     def update(self: dict, m: Mapping[Any, Any], **kwargs) -> dict:
#         dict.update(self, m)
#         return self
#
#     def values(self: dict) -> List[Any]:
#         return list(dict.values(self))
#
#     def del_(self: dict, key: Any) -> dict:
#         del self[key]
#         return self


