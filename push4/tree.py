from typing import Sequence, Optional, Tuple

from push4.expression import Expression, FunctionExpression, LiteralExpression, RegisterExpression


class Node:

    def __init__(self, expression: Expression, children: Optional[Sequence["Node"]] = None):
        # Validate the DAG node.
        if isinstance(expression, FunctionExpression):
            assert expression.arity() == len(children), "Incorrect number of child nodes."
            for idx, expected_type in enumerate(expression.input_types):
                actual_type = children[idx].data_type
                if not expected_type == actual_type:
                    raise ValueError("Child in position {i} has incorrect return type {t}. Expected {e}.".format(
                        i=idx,
                        t=actual_type,
                        e=expected_type
                    ))
        self.expression = expression
        self.children = children
        if children is None:
            self.children = []
        self.data_type = expression.return_type

    def eval(self, registry: Sequence):
        if isinstance(self.expression, FunctionExpression):
            args = []
            for child in self.children:
                args.append(child.eval(registry))
            return self.expression.fn(*args)
        elif isinstance(self.expression, LiteralExpression):
            return self.expression.value
        elif isinstance(self.expression, RegisterExpression):
            return registry[self.expression.position]
        else:
            raise ValueError("Node with invalid Expression. Got {}.".format(type(self.expression)))

    # @TODO: Add indentation.
    def to_code(self) -> str:
        if isinstance(self.expression, FunctionExpression):
            return "{name}({args})".format(
                name=self.expression.name,
                args=", ".join([child.to_code() for child in self.children])
            )
        else:
            return self.expression.name

    def pprint(self, depth: int = 0):
        print(" | " * depth, "-", str(self.expression))
        for child in self.children:
            child.pprint(depth + 1)

    def __repr__(self):
        return "Node<" + str(self.expression) + ">"


class ExpressionTree:

    def __init__(self, root: Node):
        self.root = root
        self.return_type = root.data_type

    def eval(self, *args):
        # @TODO: Validate that input types and registry match up.
        return self.root.eval(args)

    def to_code(self, function_name: str, args: Sequence[Tuple[str, type]]) -> str:
        return (
            "def {fn}({a}) -> {r}:\n"
            "    return {code}"
        ).format(
            fn=function_name,
            a=", ".join([nm + ": " + typ.__name__ for nm, typ in args]),
            r=self.return_type.__name__,
            code=self.root.to_code()
        )

    def pprint(self):
        self.root.pprint()
