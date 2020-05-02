import lib.ast as ast
from lib.token import Type
from lib.error import ParseError
from lib.scanner import Scanner
from lib.ast import ExpressionStatement


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.errors = []
        self.current = 0

    def parse(self):
        return (self.program(), self.errors)

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
        if self.matches(type):
            return self.advance()

        raise self.error(self.peek(), message)

    def error(self, token, message):
        error = ParseError(token, message)
        self.errors.append(error)
        return error

    def synchronize(self, e):
        while not self.at_end():
            if self.peek().type == Type.SEMICOLON:
                self.advance()
                return

            if self.peek().type in (
                Type.CLASS,
                Type.FUN,
                Type.VAR,
                Type.FOR,
                Type.IF,
                Type.WHILE,
                Type.PRINT,
                Type.RETURN,
            ):
                return

            self.advance()

    """ Rules """

    def program(self):
        statements = []

        while not self.at_end():
            statements.append(self.declaration())

        return ast.Program(statements)

    def declaration(self):
        try:
            if self.match_any(Type.VAR):
                return self.variable_declaration()

            return self.statement()
        except ParseError as e:
            self.synchronize(e)
            return None

    def variable_declaration(self):
        identifier = self.consume(Type.IDENTIFIER, "Expected variable name")
        initializer = self.expression() if self.match_any(Type.EQUAL) else None
        self.consume(Type.SEMICOLON, "Expected semicolon after variable declaration")
        return ast.VariableDeclaration(identifier, initializer)

    def statement(self):
        if self.match_any(Type.WHILE):
            return self.while_statement()

        if self.match_any(Type.FOR):
            return self.for_statement()

        if self.match_any(Type.IF):
            return self.if_statement()

        if self.match_any(Type.PRINT):
            return self.print_statement()

        if self.match_any(Type.LEFT_BRACE):
            return self.block()

        return self.expression_statement()

    def block(self):
        statements = []

        while not self.at_end() and not self.matches(Type.RIGHT_BRACE):
            statements.append(self.declaration())

        self.consume(Type.RIGHT_BRACE, "Expected closing brace")

        return ast.Block(statements)

    def expression_statement(self):
        expr = self.expression()
        self.consume(Type.SEMICOLON, "Expected semicolon after statement")
        return ast.ExpressionStatement(expr)

    def print_statement(self):
        exprs = [self.expression()]

        while self.match_any(Type.COMMA):
            exprs = exprs + [self.expression()]

        self.consume(Type.SEMICOLON, "Expected semicolon after statement")
        return ast.PrintStatement(exprs)

    def if_statement(self):
        self.consume(Type.LEFT_PAREN, "Expected left parenthesis on IF statement")
        test = self.expression()
        self.consume(Type.RIGHT_PAREN, "Expected right parenthesis on IF statement")
        then = self.statement()
        neht = self.statement() if self.match_any(Type.ELSE) else None
        return ast.IfStatement(test, then, neht)

    def while_statement(self):
        token = self.previous()
        self.consume(Type.LEFT_PAREN, "Expected left parenthesis on IF statement")
        test = self.expression()
        self.consume(Type.RIGHT_PAREN, "Expected right parenthesis on IF statement")
        body = self.statement()
        return ast.WhileStatement(token, test, body)

    def for_statement(self):
        token = self.previous()
        self.consume(Type.LEFT_PAREN, "Expected left parenthesis on FOR statement")

        initializer = None
        if self.match_any(Type.SEMICOLON):
            initializer = None
        elif self.match_any(Type.VAR):
            initializer = self.variable_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.matches(Type.SEMICOLON):
            condition = self.expression()
        self.consume(Type.SEMICOLON, "Expected semicolon after loop condition")

        increment = None
        if not self.matches(Type.RIGHT_PAREN):
            increment = ast.ExpressionStatement(self.expression())
        self.consume(Type.RIGHT_PAREN, "Expected right parenthesis on FOR statement")

        body = self.statement()

        statements = []
        while_body = []

        if len(body.statements) > 0:
            while_body.append(body)

        if initializer:
            statements.append(initializer)

        if increment:
            while_body.append(increment)

        test = condition if condition is not None else ast.LiteralExpression(True)
        statements.append(ast.WhileStatement(token, test, ast.Block(while_body)))

        return ast.Block(statements)

    def expression(self):
        return self.assignment()

    def assignment(self):
        left = self.ternary()

        if self.match_any(Type.EQUAL):
            token = self.previous()
            right = self.assignment()

            if isinstance(left, ast.VariableExpression):
                return ast.AssignmentExpression(left.variable, token, right)

            raise self.error(token, "Invalid assignment target")

        return left

    def ternary(self):
        expr = self.logical_or()

        while self.match_any(Type.QUESTION_MARK):
            operator = self.previous()
            then = self.logical_or()
            self.consume(Type.COLON, "Expected colon in ternary")
            nhet = self.ternary()
            expr = ast.TernaryExpression(expr, operator, then, nhet)

        return expr

    def logical_or(self):
        expr = self.logical_and()

        while self.match_any(Type.OR):
            token = self.previous()
            right = self.logical_and()
            expr = ast.LogicalExpression(expr, token, right)

        return expr

    def logical_and(self):
        expr = self.equality()

        while self.match_any(Type.AND):
            token = self.previous()
            right = self.equality()
            expr = ast.LogicalExpression(expr, token, right)

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

        return self.call()

    def call(self):
        expr = self.primary()

        while True:
            if self.match_any(Type.LEFT_PAREN):
                arguments = []

                if not self.matches(Type.RIGHT_PAREN):
                    arguments.append(self.expression())

                    while self.match_any(Type.COMMA):
                        if len(arguments) >= 255:
                            self.error(
                                self.peek(), "Maximum argument count of 255 exceeded"
                            )

                        arguments.append(self.expression())

                self.consume(Type.RIGHT_PAREN, "Expected closing parenthesis")
                token = self.previous()

                expr = ast.CallExpression(expr, token, arguments)
            else:
                break

        return expr

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
        if self.match_any(Type.IDENTIFIER):
            return ast.VariableExpression(self.previous())

        raise self.error(self.peek(), "Expected expression")

    @staticmethod
    def parse_code(code):
        (tokens, scan_errors) = Scanner(code).scan()
        for error in scan_errors:
            raise error

        (program, parse_errors) = Parser(tokens).parse()
        for error in parse_errors:
            raise error

        return program

    @staticmethod
    def parse_expr(code):
        statement = Parser.parse_code(f"{code};").statements[0]

        if not isinstance(statement, ExpressionStatement):
            raise ParseError(None, "Failed parsing expression")

        return statement.expression
