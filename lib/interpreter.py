from lib.token import Type
from lib.stringify import stringify
from lib.ast import (
    Program,
    VariableDeclaration,
    ExpressionStatement,
    PrintStatement,
    BinaryExpression,
    UnaryExpression,
    LiteralExpression,
    GroupingExpression,
    TernaryExpression,
    VariableExpression,
)
from lib.error import RuntimeError, TypeError
from lib.environment import Environment


class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.env = Environment()

    def interpret(self):
        for statement in self.ast.statements:
            self.execute(statement)

    def execute(self, statement):
        if isinstance(statement, ExpressionStatement):
            self.evaluate(statement.expression)
            return None

        if isinstance(statement, PrintStatement):
            print(*[stringify(self.evaluate(e)) for e in statement.expressions])
            return None

        if isinstance(statement, VariableDeclaration):
            value = (
                self.evaluate(statement.initializer)
                if statement.initializer != None
                else None
            )
            self.env.define(statement.identifier, value)
            return None

        raise ValueError(
            "[interpreter] Unsupported statement type [%s]"
            % statement.__class__.__name__
        )

    def evaluate(self, expr):
        if isinstance(expr, LiteralExpression):
            return expr.value

        if isinstance(expr, GroupingExpression):
            return self.evaluate(expr.expression)

        if isinstance(expr, UnaryExpression):
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

        if isinstance(expr, BinaryExpression):
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

        if isinstance(expr, TernaryExpression):
            test = self.evaluate(expr.test)
            Assert.operand_type(test, [bool], expr.operator)

            if test:
                return self.evaluate(expr.then)
            else:
                return self.evaluate(expr.neht)

        if isinstance(expr, VariableExpression):
            return self.env.get(expr.variable)

        raise ValueError(
            "[interpreter] Unsupported expression type [%s]" % expr.__class__.__name__
        )


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
