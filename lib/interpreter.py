from lib.token import Type
from lib.stringify import stringify, stringify_type, stringify_types
from lib.statement import Program, ExpressionStatement, PrintStatement
from lib.expression import (
    BinaryExpression,
    UnaryExpression,
    LiteralExpression,
    GroupingExpression,
    TernaryExpression,
)


class RuntimeError(ValueError):
    pass


class TypeError(RuntimeError):
    def __init__(self, token, message):
        self.token = token
        self.message = message

    @staticmethod
    def invalid_operand(token, value, types):
        return TypeError(
            token,
            "Operand of (%s) must be of type %s, %s given"
            % (
                token.lexeme,
                " or ".join(stringify_types(types)),
                stringify_type(type(value)),
            ),
        )

    @staticmethod
    def operand_mismatch(token, value1, value2):
        return TypeError(
            token,
            "Operands of (%s) must be of the same type. %s and %s given"
            % (
                token.lexeme,
                stringify_type(type(value1)),
                stringify_type(type(value2)),
            ),
        )

    @staticmethod
    def invalid_operands(token, value, types):
        return TypeError(
            token,
            "Operands of (%s) must be of type %s, %s given"
            % (
                token.lexeme,
                " or ".join(stringify_types(types)),
                stringify_type(type(value)),
            ),
        )


class Interpreter:
    def __init__(self, ast):
        self.ast = ast

    def interpret(self):
        try:
            for statement in self.ast.statements:
                self.execute(statement)

            return (None, None)
        except RuntimeError as e:
            return (None, e)

    def execute(self, statement):
        if isinstance(statement, ExpressionStatement):
            self.evaluate(statement.expression)
            return None

        if isinstance(statement, PrintStatement):
            value = self.evaluate(statement.expression)
            print(stringify(value))
            return None

        raise ValueError(
            "[interpreter] Unsupported statement type [%s]"
            % self.ast.__class__.__name__
        )

    def evaluate(self, ast):
        if isinstance(ast, LiteralExpression):
            return ast.value

        if isinstance(ast, GroupingExpression):
            return self.evaluate(ast.expression)

        if isinstance(ast, UnaryExpression):
            operator, value = ast.operator, self.evaluate(ast.right)

            if ast.operator.type == Type.MINUS:
                Assert.operand_type(value, [int, float], operator)
                return -value
            elif ast.operator.type == Type.BANG:
                Assert.operand_type(value, [bool], operator)
                return not value
            else:
                raise ValueError(
                    "[interpreter] Unsupported operator [%s] in unary expression"
                    % ast.operator.lexeme
                )

        if isinstance(ast, BinaryExpression):
            left, right = self.evaluate(ast.left), self.evaluate(ast.right)

            if ast.operator.type == Type.PLUS:
                Assert.operand_types(left, right, [int, float, str], ast.operator)
                return left + right
            elif ast.operator.type == Type.MINUS:
                Assert.operand_types(left, right, [int, float, str], ast.operator)
                if isinstance(left, str) and isinstance(right, str):
                    return left.replace(right, "")

                return left - right
            elif ast.operator.type == Type.STAR:
                Assert.operand_types(left, right, [int, float], ast.operator)
                return left * right
            elif ast.operator.type == Type.SLASH:
                Assert.operand_types(left, right, [int, float], ast.operator)
                return left / right
            elif ast.operator.type == Type.GREATER:
                Assert.operand_types(left, right, [int, float], ast.operator)
                return left > right
            elif ast.operator.type == Type.LESS:
                Assert.operand_types(left, right, [int, float], ast.operator)
                return left < right
            elif ast.operator.type == Type.GREATER_EQUAL:
                Assert.operand_types(left, right, [int, float], ast.operator)
                return left >= right
            elif ast.operator.type == Type.LESS_EQUAL:
                Assert.operand_types(left, right, [int, float], ast.operator)
                return left <= right
            elif ast.operator.type == Type.EQUAL_EQUAL:
                return left == right
            elif ast.operator.type == Type.BANG_EQUAL:
                return left != right
            else:
                raise ValueError(
                    "[interpreter] Operator [%s] not supported in binary expressions"
                    % ast.operator.lexeme
                )

        if isinstance(ast, TernaryExpression):
            test = self.evaluate(ast.test)
            Assert.operand_type(test, [bool], ast.operator)

            if test:
                return self.evaluate(ast.then)
            else:
                return self.evaluate(ast.neht)

        raise ValueError(
            "[interpreter] Unsupported AST type [%s]" % self.ast.__class__.__name__
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
