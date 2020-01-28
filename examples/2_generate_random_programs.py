from __future__ import annotations

from pyrsistent import CheckedPVector

from push4.gp.soup import Soup
from push4.gp.spawn import Spawner
from push4.lang.push import Push


class NatInt:

    def __init__(self, underlying: int):
        assert underlying >= 0, "Cannot make NatInt from negative int."
        self.underlying = underlying

    def to_int(self: NatInt) -> int:
        return self.underlying

    def add(self: NatInt, other: NatInt) -> NatInt:
        return NatInt(self.underlying + other.underlying)

    def sub(self: NatInt, other: NatInt) -> NatInt:
        return NatInt(max(self.underlying - other.underlying, 0))

    def mult(self: NatInt, other: NatInt) -> NatInt:
        return NatInt(self.underlying * other.underlying)

    def div(self: NatInt, other: NatInt):
        if other.underlying == 0:
            return NatInt(0)
        return NatInt(int(self.underlying / other.underlying))

    def __repr__(self):
        return "NatInt(" + str(self.underlying) + ")"


class StringList(CheckedPVector):
    __type__ = str

    def size(self: StringList) -> NatInt:
        return NatInt(len(self))

    def add(self: StringList, s: str) -> StringList:
        return self.append(s)

    def take(self: StringList, n: NatInt) -> StringList:
        return self[:n.underlying]

    def drop(self: StringList, n: NatInt) -> StringList:
        return self[n.underlying:]


soup = (
    Soup()
    .register_class(NatInt)
    .register_class(StringList)
    .register_constant(NatInt(2))
    .register_input("my_list", StringList)
)
spawner = Spawner(soup)


if __name__ == "__main__":

    push_code = spawner.spawn_push_code(10, 20)
    print("Push Code:", push_code)

    program = Push().compile(push_code, StringList, True)
    if program is None:
        print("Push code did not produce a program that returns the correct type!")
    else:
        print()
        print("Output type:", program.return_type())
        print()
        program.pprint()

        print()
        print("Testing Program")
        print(program.eval(my_list=StringList.create(["a", "b", "c", "d"])))

        print()
        print(program.to_def("my_function", ["my_list"]))
