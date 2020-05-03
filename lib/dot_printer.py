from imgcat import imgcat
from textwrap import indent
from graphviz import Source
from lib import ast
from lib.token import Token, Type


def dot_node(node, label, children=[]):
    values = []

    values.append('%s [label="%s"]' % (id(node), label))

    if isinstance(children, list):
        for child in children:
            if child is None:
                continue

            values.append(to_dot(child))
            values.append(dot_transition(node, child))
    elif isinstance(children, dict):
        for label, child in children.items():
            if child is None:
                continue

            if isinstance(child, list):
                for (i, c) in enumerate(child):
                    values.append(to_dot(c))
                    values.append(dot_transition(node, c, "argument #%s" % i))
            else:
                values.append(dot_transition(node, child, label))
                values.append(to_dot(child))
    else:
        values.append(to_dot(children))
        values.append(dot_transition(node, children))

    return "\n".join(values)


def dot_transition(a, b, label=None):
    if label:
        return '%s -> %s [label="%s"]' % (id(a), id(b), label)

    return "%s -> %s" % (id(a), id(b))


def dot_block(name, body):
    return "%s {\n%s\n}" % (name, indent(body, "\t"))


def dot_digraph(node):
    return dot_block("digraph", to_dot(node))


def to_dot(node):
    if node is None:
        return ""

    if isinstance(node, ast.Program):
        return dot_node(node, "Program", node.statements)

    if isinstance(node, ast.VariableDeclaration):
        return dot_node(
            node, "VariableDeclaration(%s)" % node.identifier.lexeme, node.initializer
        )

    if isinstance(node, ast.FunctionDeclaration):
        return dot_node(
            node,
            "FunctionDeclaration(%s)(%s)"
            % (node.name.lexeme, ", ".join([p.lexeme for p in node.parameters])),
            node.body,
        )

    if isinstance(node, ast.Block):
        return dot_node(node, "Block", node.statements)

    if isinstance(node, ast.IfStatement):
        return dot_node(
            node,
            "IfStatement",
            {"condition": node.test, "then": node.then, "else": node.neht},
        )

    if isinstance(node, ast.WhileStatement):
        return dot_node(node, "WhileStatement", node.body)

    if isinstance(node, ast.ReturnStatement):
        return dot_node(node, "ReturnStatement", node.expression)

    if isinstance(node, ast.PrintStatement):
        return dot_node(node, "PrintStatement", node.expressions)

    if isinstance(node, ast.ExpressionStatement):
        return dot_node(node, "ExpressionStatement", node.expression)

    if isinstance(node, ast.AssignmentExpression):
        return dot_node(node, "AssignmentExpression(%s)" % node.left.lexeme, node.right)

    if isinstance(node, ast.GroupingExpression):
        return dot_node(node, "GroupingExpression", node.expression)

    if isinstance(node, ast.LogicalExpression):
        return dot_node(node, "LogicalExpression", [node.left, node.right])

    if isinstance(node, ast.CallExpression):
        return dot_node(
            node,
            "CallExpression",
            {"callee": node.callee, "arguments": node.arguments},
        )

    if isinstance(node, ast.UnaryExpression):
        return dot_node(node, "UnaryExpression(%s)" % node.operator.lexeme, node.right)

    if isinstance(node, ast.BinaryExpression):
        return dot_node(
            node,
            "BinaryExpression(%s)" % node.operator.lexeme,
            [node.left, node.right],
        )

    if isinstance(node, ast.VariableExpression):
        return dot_node(node, "VariableExpression(%s)" % node.variable.lexeme)

    if isinstance(node, ast.LiteralExpression):
        return dot_node(node, "LiteralExpression(%s)" % node.value)

    if isinstance(node, ast.FunctionExpression):
        return dot_node(
            node,
            "FunctionExpression(%s)" % ", ".join([p.lexeme for p in node.parameters]),
            node.body,
        )

    if isinstance(node, ast.LambdaExpression):
        return dot_node(
            node,
            "LambdaExpression(%s)" % ", ".join([p.lexeme for p in node.parameters]),
            node.expression,
        )

    if isinstance(node, ast.TernaryExpression):
        return dot_node(
            node,
            "TernaryExpression",
            {"test": node.test, "then": node.then, "else": node.neht},
        )

    raise ValueError("[dot printer] AST node [%s] not supported" % node.__class__)


def ast_to_dot(node):
    return dot_digraph(node)


def ast_to_image(ast):
    imgcat(Source(ast_to_dot(ast), format="png").pipe())
