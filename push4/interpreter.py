from typing import Sequence, Optional, Any, Callable, Tuple

from push4.tree import ExpressionTree, Node
from push4.expression import Expression, FunctionExpression, clean_type_name, expression_from_function, \
    RegisterExpression, LiteralExpression


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

    def __repr__(self):
        self_r = list(self)[::-1]
        return self_r.__repr__()

    def __eq__(self, other):
        if not isinstance(other, PushStack):
            return False
        return list(self) == list(other)


class PushState(dict):

    def __init__(self):
        super().__init__()

    def add(self, node: Node):
        stack = self.get(node.data_type, PushStack())
        stack.append(node)
        self[node.data_type] = stack

    def get_top_node(self, data_type: type) -> Node:
        return self[data_type].top()

    def observe_stacks(self, types: Sequence[type]) -> list:
        values = []
        counts = {}
        for typ in types:
            ndx = counts.get(typ, 0)
            values.append(self[typ].nth(ndx))
            counts[typ] = ndx + 1
        return values

    def pop_from_stacks(self, types: Sequence[type]) -> list:
        values = []
        for typ in types:
            val = self[typ].top()
            values.append(val)
            self[typ].pop()
        return values

    def pprint(self):
        for typ, stack in self.items():
            print(clean_type_name(typ), ":", stack)


def _process_expression(state: PushState, expression: Expression) -> PushState:
    if isinstance(expression, FunctionExpression):
        # Skip expression if there are missing stacks.
        for typ in set(expression.input_types):
            if typ not in state.keys():
                return state

        children = state.observe_stacks(expression.input_types)
        if None in children:
            return state

        node = Node(expression, children)
        state.pop_from_stacks(expression.input_types)
        state.add(node)
    else:
        state.add(Node(expression))
    return state


def _gene_to_expression(gene: Any) -> Expression:
    if isinstance(gene, Callable):
        return expression_from_function(gene)
    elif isinstance(gene, Tuple):
        return RegisterExpression(*gene)
    else:
        return LiteralExpression(gene)


def run(genome: Sequence[Any], output_type: type) -> ExpressionTree:
    step = 0
    state = PushState()
    for gene in genome:
        expression = _gene_to_expression(gene)
        print(step, "- Evaluating", expression)
        state.pprint()
        state = _process_expression(state, expression)
        print()
        step += 1
    return ExpressionTree(state.get_top_node(output_type))
