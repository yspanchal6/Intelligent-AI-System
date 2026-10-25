
# Task Engine for Intelligent AI System

import ast
import operator


# Allow only basic arithmetic operations.
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def evaluate_expression(expression):
    """Safely evaluate a basic arithmetic expression."""

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            left = evaluate(node.left)
            right = evaluate(node.right)

            # Prevent excessive exponent calculations.
            if isinstance(node.op, ast.Pow):
                if abs(right) > 10 or abs(left) > 1_000_000:
                    raise ValueError("Exponent is too large.")

            result = OPERATORS[type(node.op)](left, right)

            if isinstance(result, (int, float)) and abs(result) > 1e100:
                raise ValueError("Result is too large.")

            return result

        if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](evaluate(node.operand))

        raise ValueError("Unsupported expression.")

    if len(expression) > 100:
        raise ValueError("Expression is too long.")

    tree = ast.parse(expression, mode="eval")
    result = evaluate(tree.body)

    if isinstance(result, float) and not __import__("math").isfinite(result):
        raise ValueError("Result is not finite.")

    return result
