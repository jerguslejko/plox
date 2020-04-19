import os
import tempfile
from functools import reduce
from lib.token import Token, Type
from lib.ast import (
    Block,
    ExpressionStatement,
    VariableDeclaration,
    PrintStatement,
    WhileStatement,
    BinaryExpression,
    UnaryExpression,
    LiteralExpression,
    GroupingExpression,
    TernaryExpression,
    VariableExpression,
    AssignmentExpression,
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

    if isinstance(expr, VariableExpression):
        return [
            '%s [label="VariableExpression(%s)"]' % (id(expr), expr.variable.lexeme),
        ]

    if isinstance(expr, AssignmentExpression):
        return [
            '%s [label="AssignmentExpression(%s)"]' % (id(expr), expr.left.lexeme),
            "%s -> %s" % (id(expr), id(expr.right)),
        ] + print_expr(expr.right)

    raise ValueError("Expression [%s] not supported" % type(expr))


def print_statement(statement):
    if isinstance(statement, ExpressionStatement):
        return [
            '%s [label="ExpressionStatement"]' % id(statement),
            "%s -> %s" % (id(statement), id(statement.expression)),
        ] + print_expr(statement.expression)

    if isinstance(statement, PrintStatement):
        return reduce(
            lambda xs, expr: xs + print_expr(expr),
            statement.expressions,
            [
                '%s [label="PrintStatement"]' % id(statement),
                "%s -> { %s }"
                % (
                    id(statement),
                    ", ".join(map(lambda e: str(id(e)), statement.expressions)),
                ),
            ],
        )

    if isinstance(statement, VariableDeclaration):
        return [
            '%s [label="VariableDeclaration(%s)"]'
            % (id(statement), statement.identifier.lexeme),
            "%s" % id(statement)
            if statement.initializer is None
            else "%s -> %s" % (id(statement), id(statement.initializer)),
        ] + ([] if statement.initializer is None else print_expr(statement.initializer))

    if isinstance(statement, Block):
        return reduce(
            lambda xs, statement: xs + print_statement(statement),
            statement.statements,
            [
                '%s [label="Block"]' % id(statement),
                "%s -> { %s }"
                % (
                    id(statement),
                    ", ".join(map(lambda s: str(id(s)), statement.statements)),
                ),
            ],
        )

    if isinstance(statement, WhileStatement):
        return (
            [
                '%s [label="WhileStatement"]' % id(statement),
                "%s -> { %s, %s }"
                % (id(statement), id(statement.test), id(statement.body)),
            ]
            + print_expr(statement.test)
            + print_statement(statement.body)
        )

    raise ValueError("Statement [%s] not supported" % type(statement))


def print_program(ast):
    return reduce(
        lambda xs, statement: xs + print_statement(statement),
        ast.statements,
        [
            '%s [label="Program"]' % id(ast),
            "%s -> { %s }"
            % (id(ast), ", ".join(map(lambda s: str(id(s)), ast.statements))),
        ],
    )


def print_ast(ast):
    return "digraph { %s }" % "; ".join(print_program(ast))


def show_ast(ast):
    file = tempfile.NamedTemporaryFile(mode="w", delete=False)
    file.write(print_ast(ast))
    file.close()
    os.system(r"dot -Tpng -Gsize=18,18\! -Gdpi=100 %s | imgcat" % (file.name))
