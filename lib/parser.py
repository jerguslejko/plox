import lib.ast as ast
from lib.token import Type

"""
GRAMMAR:

program    → statement* EOF
statement  → expr_stmt | print_stmt
print_stmt → "print" expression ";"
expr_stmt  → expression ";"
expression → literal | unary | binary | grouping | ternary | primary
literal    → NUMBER | STRING | "false" | "true" | "nil"
grouping   → "(" expression ")"
unary      → ( "-" | "!" ) expression
binary     → expression operator expression
ternary    → expression "?" expression ":" expression
operator   → "==" | "!=" | "<" | "<=" | ">" | ">="
           | "+"  | "-"  | "*" | "/" | ","
primary    → NUMBER | STRING | "false" | "true" | "nil"
           | "(" expression ")"
"""


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.errors = []
        self.current = 0

    def parse(self):
        try:
            statements = []

            while not self.at_end():
                statements.append(self.program())

            return (ast.Program(statements), [])
        except ParseError:
            return (None, self.errors)

    def advance(self):
        self.current += 1
        return self.previous()

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        if self.current == 0:
            raise ValueError("cannot look at previous token when at position 0")

        return self.tokens[self.current - 1]

    def match_any(self, *types):
        for type in types:
            if self.matches(type):
                self.advance()
                return True

        return False

    def matches(self, type):
        if self.at_end():
            return False

        return self.peek().type == type

    def at_end(self):
        return self.tokens[self.current].type == Type.EOF

    def consume(self, type, message):
        if self.check(type):
            return self.advance()

        raise self.error(self.peek(), message)

    def error(self, token, message):
        self.errors.append((token, message))
        return ParseError()

    def check(self, type):
        if self.at_end():
            return False

        return self.peek().type == type

    """ Rules """

    def program(self):
        if self.match_any(Type.PRINT):
            return self.print_statement()

        return self.statement()

    def statement(self):
        expr = self.expression()
        self.consume(Type.SEMICOLON, "Expected semicolon after statement")
        return ast.ExpressionStatement(expr)

    def print_statement(self):
        exprs = [self.expression()]

        while self.match_any(Type.COMMA):
            exprs = exprs + [self.expression()]

        self.consume(Type.SEMICOLON, "Expected semicolon after statement")
        return ast.PrintStatement(exprs)

    def expression(self):
        return self.ternary()

    def ternary(self):
        expr = self.equality()

        while self.match_any(Type.QUESTION_MARK):
            operator = self.previous()
            then = self.equality()
            self.consume(Type.COLON, "Expected colon in ternary")
            nhet = self.ternary()
            expr = ast.TernaryExpression(expr, operator, then, nhet)

        return expr

    def equality(self):
        expr = self.comparison()

        while self.match_any(Type.BANG_EQUAL, Type.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()

            expr = ast.BinaryExpression(expr, operator, right)

        return expr

    def comparison(self):
        expr = self.addition()

        while self.match_any(
            Type.GREATER, Type.GREATER_EQUAL, Type.LESS, Type.LESS_EQUAL
        ):
            operator = self.previous()
            right = self.addition()

            expr = ast.BinaryExpression(expr, operator, right)

        return expr

    def addition(self):
        expr = self.multiplication()

        while self.match_any(Type.PLUS, Type.MINUS):
            operator = self.previous()
            right = self.multiplication()

            expr = ast.BinaryExpression(expr, operator, right)

        return expr

    def multiplication(self):
        expr = self.unary()

        while self.match_any(Type.STAR, Type.SLASH):
            operator = self.previous()
            right = self.unary()

            expr = ast.BinaryExpression(expr, operator, right)

        return expr

    def unary(self):
        if self.match_any(Type.BANG, Type.MINUS):
            return ast.UnaryExpression(self.previous(), self.unary())

        return self.primary()

    def primary(self):
        if self.match_any(Type.TRUE):
            return ast.LiteralExpression(True)
        if self.match_any(Type.FALSE):
            return ast.LiteralExpression(False)
        if self.match_any(Type.NIL):
            return ast.LiteralExpression(None)
        if self.match_any(Type.NUMBER, Type.STRING):
            return ast.LiteralExpression(self.previous().literal)
        if self.match_any(Type.LEFT_PAREN):
            expr = self.expression()
            self.consume(Type.RIGHT_PAREN, "Expected ')' after expression")
            return ast.GroupingExpression(expr)

        raise self.error(self.peek(), "Expected expression")


class ParseError(RuntimeError):
    pass
