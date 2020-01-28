import sys
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
from typing import Sequence, Type

from push4.lang.expr import Expression


class Dag:

    def __init__(self, root: Expression):
        self.root = deepcopy(root)
        self.root.reify(include_children=True)
        self.stdout_buffer = StringIO()

    def stdout(self) -> str:
        return self.stdout_buffer.getvalue()

    def eval(self, **kwargs):
        self.stdout_buffer = StringIO()
        with redirect_stdout(self.stdout_buffer):
            ret = self.root.eval(**kwargs)
        return ret

    def return_type(self) -> Type:
        return self.root.dtype()

    def to_code(self):
        return self.root.to_code()

    def to_def(self, name: str, arg_names: Sequence[str]) -> str:
        return "def {nm}({args}):\n    return {code}".format(
            nm=name,
            args=", ".join(arg_names),
            code=self.root.to_code()
        )

    def pprint(self):
        self.root.pprint()

    def __eq__(self, other):
        return isinstance(other, Dag) and self.root == other.root
