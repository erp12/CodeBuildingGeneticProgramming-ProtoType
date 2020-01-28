from copy import copy
from io import StringIO
from typing import Optional, Type, Sequence, Mapping, MutableSequence, List

from pyrsistent import m, PVector
from pytypes import is_subtype, get_Generic_itemtype

from push4.collections import POMap
from push4.lang.dag import Dag
from push4.lang.expr import Expression, Constant, Function, Input, FunctionLike
from push4.lang.hof import HOF, Closure, LocalInput
from push4.lang.reify import TypeReifier, Signature


class PushStack(list):

    def is_empty(self) -> bool:
        return len(self) == 0

    def push(self, value):
        self.append(value)
        return self

    def pop(self, index: Optional[int] = None):
        if index is None:
            return super().pop()
        else:
            return super().pop((len(self) - 1) - index)

    def nth(self, position: int):
        if len(self) <= position:
            return None
        elif len(self) == 0:
            return None
        else:
            return self[(len(self) - 1) - position]

    def take(self, n: int):
        if n < 0:
            return []
        return self[:-(n + 1):-1]

    def top(self):
        if len(self) > 0:
            return self[-1]

    def insert(self, position: int, value):
        super().insert(len(self) - position, value)
        return self

    def set_nth(self, position: int, value):
        self[len(self) - 1 - position] = value
        return self

    def flush(self):
        del self[:]
        return self

    def pprint(self):
        for el in self[::-1]:
            print("\t", el)

    def __repr__(self):
        self_r = list(self)[::-1]
        return self_r.__repr__()

    def __eq__(self, other):
        if not isinstance(other, PushStack):
            return False
        return list(self) == list(other)


class Push:

    def __init__(self, allow_local_args: bool = False):
        self.dag_stack = PushStack()
        self.closure_stack = PushStack()
        self.allow_local_args = allow_local_args

    def _pop_top_valid(self, typ: Type) -> Optional[Expression]:
        for ndx, el in enumerate(self.dag_stack[::-1]):
            if is_subtype(el.dtype(), typ) and el.depth < 50:
                return self.dag_stack.pop(ndx)
        return None

    def _pop_children(self, signature: Signature, reifier: TypeReifier = None) -> POMap:
        old_stack = copy(self.dag_stack)
        children = POMap()
        reified_sig = signature
        for child_name in signature.args.keys():
            typ = reified_sig.args[child_name]
            child = self._pop_top_valid(typ)
            if child is None:
                self.dag_stack = old_stack
                return None
            children = children.add(child_name, child)
            if reifier is not None:
                child_types = {nm: child.dtype() for nm, child in children.items()}
                reified_sig = reifier.reify(reified_sig, child_types)
        return children

    def _pop_top_valid_closure_as_dag(self, el_type: type, n_args: int, ret: type) -> Optional[Dag]:
        for ndx, closure in enumerate(self.closure_stack[::-1]):
            clean_func_def = []
            for e in closure.func_def:
                if isinstance(e, LocalInput):
                    fixed_local_input = LocalInput(e.ndx % n_args, el_type)
                    clean_func_def.append(fixed_local_input)
                else:
                    clean_func_def.append(e)
            # print(">>> IN >>>")
            dag = Push(allow_local_args=True).compile(clean_func_def, ret)
            # print("<<< OUT <<<")
            if dag is not None:
                self.closure_stack.pop(ndx)
                return dag
        return None

    def process_expr(self, expr: Expression, verbose: bool = False):
        if verbose:
            print()
            print("Processing:", expr)
            print("DAG Stack:")
            self.dag_stack.pprint()
            print("Closure Stack:")
            self.closure_stack.pprint()
        if isinstance(expr, Constant):
            self.dag_stack.push(expr)
        elif isinstance(expr, Input):
            if isinstance(expr, LocalInput):
                if self.allow_local_args:
                    self.dag_stack.push(expr)
            else:
                self.dag_stack.push(expr)
        elif isinstance(expr, FunctionLike):
            expr_copy = copy(expr)
            reifier = getattr(expr_copy, "reifier", None)
            children = self._pop_children(expr_copy.base_signature, reifier)
            if children is None:
                return
            expr_copy.add_children(children)
            expr_copy.reify()
            self.dag_stack.push(expr_copy)
        elif isinstance(expr, (PVector, List)):
            self.closure_stack.push(Closure(expr))
        elif isinstance(expr, HOF):
            old_dag_stack = copy(self.dag_stack)
            seq = self._pop_top_valid(List)
            if seq is None:
                self.dag_stack = old_dag_stack
                # print("Tried HOF - Got no seq")
                return

            el_type = get_Generic_itemtype(seq.dtype())  # NOTE: Will break on just `List`.
            old_closure_stack = copy(self.closure_stack)
            func_dag = self._pop_top_valid_closure_as_dag(el_type, *expr.inner_func_spec())
            if func_dag is None:
                self.closure_stack = old_closure_stack
                # print("Tried HOF - Got no closures out of " + str(len(self.closure_stack)))
                return

            expr.add_child("seq", seq)
            expr.add_child("func", func_dag.root)
            expr.reify()
            self.dag_stack.push(expr)
        else:
            raise ValueError("Found invalid PushCode element: " + str(expr))

    def compile(self, push_code: Sequence[Expression], output_type: type, verbose: bool = False) -> Dag:
        self.dag_stack = PushStack()
        for expr in push_code:
            self.process_expr(expr, verbose)
        if verbose:
            print()
            print("Final DAG Stack:")
            self.dag_stack.pprint()
            print("Final Closure Stack:")
            self.closure_stack.pprint()
        dag_root = self._pop_top_valid(output_type)
        if dag_root is None:
            return None
        return Dag(dag_root)
