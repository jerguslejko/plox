import os
import tempfile
from lib.token import Token, Type
from lib.expression import (
    BinaryExpression,
    UnaryExpression,
    LiteralExpression,
    GroupingExpression,
    TernaryExpression,
)


def print_expr(expr):
    if isinstance(expr, BinaryExpression):
        return (
            [
                '%s [label="BinaryExpression(%s)"]' % (id(expr), expr.operator.lexeme),
                "%s -> { %s, %s }" % (id(expr), id(expr.left), id(expr.right)),
            ]
            + print_expr(expr.left)
            + print_expr(expr.right)
        )

    if isinstance(expr, UnaryExpression):
        return [
            '%s [label="UnaryExpression(%s)"]' % (id(expr), expr.operator.lexeme),
            "%s -> %s" % (id(expr), id(expr.right)),
        ] + print_expr(expr.right)

    if isinstance(expr, LiteralExpression):
        return [
            '%s [label="LiteralExpression(%s)"]' % (id(expr), expr.value),
        ]

    if isinstance(expr, GroupingExpression):
        return [
            '%s [label="GroupingExpression"]' % id(expr),
            "%s -> %s" % (id(expr), id(expr.expression)),
        ] + print_expr(expr.expression)

    if isinstance(expr, TernaryExpression):
        return (
            [
                '%s [label="TernaryExpression"]' % id(expr),
                "%s -> { %s, %s, %s }"
                % (id(expr), id(expr.test), id(expr.then), id(expr.neht)),
            ]
            + print_expr(expr.test)
            + print_expr(expr.then)
            + print_expr(expr.neht)
        )

    raise ValueError("Expression [%s] not supported" % type(expr))


def print_ast(ast):
    return "digraph { %s }" % "; ".join(print_expr(ast))


def show_ast(ast):
    file = tempfile.NamedTemporaryFile(mode="w", delete=False)
    file.write(print_ast(ast))
    file.close()
    os.system(r"dot -Tpng -Gsize=18,18\! -Gdpi=100 %s | imgcat" % (file.name))
