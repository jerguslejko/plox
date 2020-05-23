from lib import ast
from lib.token import Type, identifier
from lib.stringify import stringify
from lib.error import RuntimeError, TypeError
from lib.resolver import Resolver
from lib.environment import Environment
from lib.scanner import Scanner
from lib.parser import Parser
from lib.io import RealPrinter, FakePrinter
from lib.function import (
    Function,
    AnonymousFunction,
    Callable,
)
from lib.globals import ClockFunction, SleepFunction


class Return(RuntimeError):
    def __init__(self, value):
        self.value = value


class Interpreter:
    printer = RealPrinter

    def __init__(self):
        self.bindings = {}
        self.globals = global_environment()
        self.env = self.globals
        self.printer = Interpreter.printer()

    def interpret(self, ast, bindings):
        self.bindings = {**self.bindings, **bindings}

        self.execute(ast)

        return self

    def lookup_variable(self, node, name):
        if node in self.bindings:
            return self.env.get_at(self.bindings[node], name)
        else:
            return self.globals.get(name)

    def execute(self, node):
        if isinstance(node, ast.Program):
            for statement in node.statements:
                self.execute(statement)
            return None

        if isinstance(node, ast.ExpressionStatement):
            self.evaluate(node.expression)
            return None

        if isinstance(node, ast.PrintStatement):
            self.printer.print(*[stringify(self.evaluate(e)) for e in node.expressions])
            return None

        if isinstance(node, ast.VariableDeclaration):
            if node.initializer != None:
                self.env.define(node.identifier, self.evaluate(node.initializer))
            else:
                self.env.define(node.identifier)

            return None

        if isinstance(node, ast.Block):
            self.execute_block(node, self.env.child())
            return None

        if isinstance(node, ast.IfStatement):
            test = self.evaluate(node.test)
            Assert.operand_type(test, [bool], None)

            if test:
                self.execute(node.then)
            else:
                if node.neht is not None:
                    self.execute(node.neht)

            return None

        if isinstance(node, ast.WhileStatement):
            test = self.evaluate(node.test)
            Assert.operand_type(test, [bool], node.token)
            while test:
                self.execute(node.body)
                test = self.evaluate(node.test)

            return None

        if isinstance(node, ast.FunctionDeclaration):
            fun = Function(node, self.env)

            self.env.define(fun.identifier(), fun)

            return None

        if isinstance(node, ast.ReturnStatement):
            raise Return(self.evaluate(node.expression))

        raise ValueError(
            "[interpreter] Unsupported node type [%s]" % node.__class__.__name__
        )

    def execute_block(self, block, env):
        previous_env = self.env

        try:
            self.env = env

            for statement in block.statements:
                self.execute(statement)
        finally:
            self.env = previous_env

    def evaluate(self, expr):
        if isinstance(expr, ast.LiteralExpression):
            return expr.value

        if isinstance(expr, ast.FunctionExpression):
            return AnonymousFunction(expr, self.env)

        if isinstance(expr, ast.LambdaExpression):
            return self.evaluate(
                ast.FunctionExpression(
                    expr.parameters,
                    ast.Block([ast.ReturnStatement(expr.expression, expr.arrow)]),
                )
            )

        if isinstance(expr, ast.GroupingExpression):
            return self.evaluate(expr.expression)

        if isinstance(expr, ast.UnaryExpression):
            operator, value = expr.operator, self.evaluate(expr.right)

            if expr.operator.type == Type.MINUS:
                Assert.operand_type(value, [int, float], operator)
                return -value
            elif expr.operator.type == Type.BANG:
                Assert.operand_type(value, [bool], operator)
                return not value
            else:
                raise ValueError(
                    "[interpreter] Unsupported operator [%s] in unary expression"
                    % expr.operator.lexeme
                )

        if isinstance(expr, ast.BinaryExpression):
            left, right = self.evaluate(expr.left), self.evaluate(expr.right)

            if expr.operator.type == Type.PLUS:
                Assert.operand_types(left, right, [int, float, str], expr.operator)
                return left + right
            elif expr.operator.type == Type.MINUS:
                Assert.operand_types(left, right, [int, float, str], expr.operator)
                if isinstance(left, str) and isinstance(right, str):
                    return left.replace(right, "")

                return left - right
            elif expr.operator.type == Type.STAR:
                Assert.operand_types(left, right, [int, float], expr.operator)
                return left * right
            elif expr.operator.type == Type.SLASH:
                Assert.operand_types(left, right, [int, float], expr.operator)
                return left / right
            elif expr.operator.type == Type.GREATER:
                Assert.operand_types(left, right, [int, float], expr.operator)
                return left > right
            elif expr.operator.type == Type.LESS:
                Assert.operand_types(left, right, [int, float], expr.operator)
                return left < right
            elif expr.operator.type == Type.GREATER_EQUAL:
                Assert.operand_types(left, right, [int, float], expr.operator)
                return left >= right
            elif expr.operator.type == Type.LESS_EQUAL:
                Assert.operand_types(left, right, [int, float], expr.operator)
                return left <= right
            elif expr.operator.type == Type.EQUAL_EQUAL:
                return left == right
            elif expr.operator.type == Type.BANG_EQUAL:
                return left != right
            else:
                raise ValueError(
                    "[interpreter] Operator [%s] not supported in binary expressions"
                    % expr.operator.lexeme
                )

        if isinstance(expr, ast.TernaryExpression):
            test = self.evaluate(expr.test)
            Assert.operand_type(test, [bool], expr.operator)

            if test:
                return self.evaluate(expr.then)
            else:
                return self.evaluate(expr.neht)

        if isinstance(expr, ast.VariableExpression):
            return self.lookup_variable(expr, expr.variable)

        if isinstance(expr, ast.AssignmentExpression):
            value = self.evaluate(expr.right)
            self.env.assign(expr.left, value)
            return value

        if isinstance(expr, ast.LogicalExpression):
            if expr.token.type == Type.OR:
                left = self.evaluate(expr.left)
                Assert.operand_type(left, [bool], expr.token)

                if left:
                    return True

                right = self.evaluate(expr.right)
                Assert.operand_type(right, [bool], expr.token)
                return right

            if expr.token.type == Type.AND:
                left = self.evaluate(expr.left)
                Assert.operand_type(left, [bool], expr.token)
                if not left:
                    return False

                right = self.evaluate(expr.right)
                Assert.operand_type(right, [bool], expr.token)
                return right

            raise ValueError("unsupported logical operator (%s)" % expr.token.lexeme)

        if isinstance(expr, ast.CallExpression):
            callee = self.evaluate(expr.callee)

            if not isinstance(callee, Callable):
                raise RuntimeError(expr.token, "Can only call functions or classes")

            arguments = list(map(self.evaluate, expr.arguments))

            if len(arguments) != callee.arity():
                raise RuntimeError(
                    expr.token,
                    "Expected %s arguments but got %s"
                    % (callee.arity(), len(arguments)),
                )

            return callee.call(self, arguments)

        raise ValueError(
            "[interpreter] Unsupported expression type [%s]" % expr.__class__.__name__
        )

    @staticmethod
    def from_code(code):
        tokens = Scanner(code).scan()
        ast = Parser(tokens).parse()
        bindings = Resolver(ast).run()
        return Interpreter().interpret(ast, bindings)

    @staticmethod
    def evaluate_expr(code):
        interpreter = Interpreter.from_code(f"{code};")
        return interpreter.evaluate(interpreter.ast.statements[0].expression)


class Assert:
    @staticmethod
    def operand_type(value, types, token):
        if type(value) not in types:
            raise TypeError.invalid_operand(token, value, types)

    def operand_types(value1, value2, types, token):
        Assert.operands_same_type(value1, value2, token)

        if type(value1) not in types:
            raise TypeError.invalid_operands(token, value1, types)

    def operands_same_type(value1, value2, token):
        if type(value1) is not type(value2):
            raise TypeError.operand_mismatch(token, value1, value2)


def global_environment():
    env = Environment()

    env.define(identifier("clock"), ClockFunction())
    env.define(identifier("sleep"), SleepFunction())

    return env
