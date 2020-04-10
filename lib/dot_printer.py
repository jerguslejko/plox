import expression as e
from token import Token, Type


def print_expr(expr):
    if isinstance(expr, e.BinaryExpression):
        return [
            '%s [label="BinaryExpression(%s)"]' % (id(expr), expr.operator.lexeme),
            '%s -> { %s, %s }' % (id(expr), id(expr.left), id(expr.right)),
        ] + print_expr(expr.left) + print_expr(expr.right)

    if isinstance(expr, e.UnaryExpression):
        return [
            '%s [label="UnaryExpression(%s)"]' % (id(expr), expr.operator.lexeme),
            '%s -> %s' % (id(expr), id(expr.right)),
        ] + print_expr(expr.right)

    if isinstance(expr, e.LiteralExpression):
        return [
            '%s [label="LiteralExpression(%s)"]' % (id(expr), expr.value),
        ]

    if isinstance(expr, e.GroupingExpression):
        return [
            '%s [label="GroupingExpression"]' % id(expr),
            '%s -> %s' % (id(expr), id(expr.expression)),
        ] + print_expr(expr.expression)

    raise ValueError("Expression [%s] not supported" % expr)


def print_ast(ast):
    return "digraph { %s }" % "; ".join(print_expr(ast))
