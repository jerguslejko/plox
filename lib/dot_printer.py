import os
import tempfile
from imgcat import imgcat
from graphviz import Source
from functools import reduce
from lib.token import Token, Type
from lib.ast import (
    Block,
    ExpressionStatement,
    ReturnStatement,
    IfStatement,
    VariableDeclaration,
    FunctionDeclaration,
    PrintStatement,
    WhileStatement,
    BinaryExpression,
    UnaryExpression,
    LiteralExpression,
    FunctionExpression,
    LambdaExpression,
    GroupingExpression,
    TernaryExpression,
    VariableExpression,
    AssignmentExpression,
    LogicalExpression,
    CallExpression,
)


def print_expr(expr):
    if isinstance(expr, LogicalExpression):
        return (
            [
                '%s [label="LogicalExpression(%s)"]' % (id(expr), expr.token.lexeme),
                "%s -> { %s, %s }" % (id(expr), id(expr.left), id(expr.right)),
            ]
            + print_expr(expr.left)
            + print_expr(expr.right)
        )

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

    if isinstance(expr, FunctionExpression):
        return [
            '%s [label="FunctionExpression(%s)"]'
            % (id(expr), ", ".join(map(lambda p: p.lexeme, expr.parameters)),),
            "%s -> %s" % (id(expr), id(expr.body)),
        ] + print_statement(expr.body)

    if isinstance(expr, LambdaExpression):
        return [
            '%s [label="LambdaExpression(%s)"]'
            % (id(expr), ", ".join(map(lambda p: p.lexeme, expr.parameters)),),
            "%s -> %s" % (id(expr), id(expr.expression)),
        ] + print_expr(expr.expression)

    if isinstance(expr, AssignmentExpression):
        return [
            '%s [label="AssignmentExpression(%s)"]' % (id(expr), expr.left.lexeme),
            "%s -> %s" % (id(expr), id(expr.right)),
        ] + print_expr(expr.right)

    if isinstance(expr, CallExpression):
        return (
            [
                '%s [label="CallExpression"]' % id(expr),
                "%s -> %s" % (id(expr), id(expr.callee)),
                'subgraph cluster_%s_callee { label="callee" %s }'
                % (id(expr), id(expr.callee)),
                "%s -> { %s }"
                % (
                    id(expr),
                    ", ".join(map(lambda e: str(id(e)), reversed(expr.arguments))),
                ),
            ]
            + print_expr(expr.callee)
            + reduce(
                lambda xs, expr: print_expr(expr) + xs,
                expr.arguments,
                [
                    'subgraph cluster_%s_arguments { label="arguments"; %s }'
                    % (id(expr), "; ".join(map(lambda e: str(id(e)), expr.arguments))),
                ],
            )
        )

    raise ValueError("Expression [%s] not supported" % type(expr))


def print_statement(statement):
    if isinstance(statement, ExpressionStatement):
        return [
            '%s [label="ExpressionStatement"]' % id(statement),
            "%s -> %s" % (id(statement), id(statement.expression)),
        ] + print_expr(statement.expression)

    if isinstance(statement, IfStatement):
        return (
            [
                '%s [label="IfStatement"]' % id(statement),
                "%s -> %s" % (id(statement), id(statement.test)),
                "%s -> %s" % (id(statement), id(statement.then)),
                (
                    "%s -> %s" % (id(statement), id(statement.neht))
                    if statement.neht
                    else None
                ),
            ]
            + print_expr(statement.test)
            + print_statement(statement.then)
            + (print_statement(statement.neht) if statement.neht else [])
        )

    if isinstance(statement, ReturnStatement):
        return [
            '%s [label="ReturnStatement"]' % id(statement),
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
        ) + [
            "subgraph cluster_%s_block { %s }"
            % (
                id(statement),
                "; ".join(map(lambda e: str(id(e)), statement.statements)),
            ),
        ]

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

    if isinstance(statement, FunctionDeclaration):
        return [
            '%s [label="FunctionDeclaration(%s)(%s)"]'
            % (
                id(statement),
                statement.name.lexeme,
                ", ".join(map(lambda p: p.lexeme, statement.parameters)),
            ),
            "%s -> %s" % (id(statement), id(statement.body)),
        ] + print_statement(statement.body)

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


def to_dot(ast):
    return "digraph { %s }" % "; ".join(filter(lambda x: x, print_program(ast)))


def show_ast(ast):
    imgcat(Source(to_dot(ast), format="png").pipe())
