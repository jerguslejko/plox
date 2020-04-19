import unittest
import lib.ast as ast
from lib.parser import Parser, ParseError
from lib.scanner import Scanner
from lib.token import Token, Type


class ParserTest(unittest.TestCase):
    def test_it_parses_literals(self):
        self.assertEqual(
            ast.LiteralExpression(1), parse_expr("1"),
        )

        self.assertEqual(
            ast.LiteralExpression(1.2), parse_expr("1.2"),
        )

        self.assertEqual(
            ast.LiteralExpression("hello"), parse_expr('"hello"'),
        )
        self.assertEqual(
            ast.LiteralExpression("hello"), parse_expr("'hello'"),
        )

        self.assertEqual(
            ast.LiteralExpression(True), parse_expr("true"),
        )

        self.assertEqual(
            ast.LiteralExpression(False), parse_expr("false"),
        )

        self.assertEqual(
            ast.LiteralExpression(None), parse_expr("nil"),
        )

        self.assertEqual(
            ast.GroupingExpression(ast.LiteralExpression(1)), parse_expr("(1)")
        )

    def test_it_parses_equality(self):
        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.EQUAL_EQUAL, "==", None, 1),
                ast.LiteralExpression(1),
            ),
            parse_expr("1 == 1"),
        )

    def test_it_parses_comparison(self):
        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.LESS, "<", None, 1),
                ast.LiteralExpression(1),
            ),
            parse_expr("1 < 1"),
        )

        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.LESS_EQUAL, "<=", None, 1),
                ast.LiteralExpression(1),
            ),
            parse_expr("1 <= 1"),
        )

        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.GREATER, ">", None, 1),
                ast.LiteralExpression(1),
            ),
            parse_expr("1 > 1"),
        )

        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.GREATER_EQUAL, ">=", None, 1),
                ast.LiteralExpression(1),
            ),
            parse_expr("1 >= 1"),
        )

    def test_it_parses_addition(self):
        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.PLUS, "+", None, 1),
                ast.LiteralExpression(1),
            ),
            parse_expr("1 + 1"),
        )

        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.MINUS, "-", None, 1),
                ast.LiteralExpression(1),
            ),
            parse_expr("1 - 1"),
        )

    def test_it_parses_multiplicate(self):
        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.STAR, "*", None, 1),
                ast.LiteralExpression(1),
            ),
            parse_expr("1 * 1"),
        )

        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.SLASH, "/", None, 1),
                ast.LiteralExpression(1),
            ),
            parse_expr("1 / 1"),
        )

    def test_it_parses_unary(self):
        self.assertEqual(
            ast.UnaryExpression(
                Token(Type.BANG, "!", None, 1), ast.LiteralExpression(True),
            ),
            parse_expr("!true"),
        )

        self.assertEqual(
            ast.UnaryExpression(
                Token(Type.MINUS, "-", None, 1), ast.LiteralExpression(42),
            ),
            parse_expr("-42"),
        )

    def test_it_respects_operator_precedence(self):
        self.assertEqual(
            ast.BinaryExpression(
                ast.BinaryExpression(
                    ast.LiteralExpression(1),
                    Token(Type.PLUS, "+", None, 1),
                    ast.BinaryExpression(
                        ast.BinaryExpression(
                            ast.LiteralExpression(2),
                            Token(Type.STAR, "*", None, 1),
                            ast.LiteralExpression(3),
                        ),
                        Token(Type.SLASH, "/", None, 1),
                        ast.UnaryExpression(
                            Token(Type.MINUS, "-", None, 1), ast.LiteralExpression(4),
                        ),
                    ),
                ),
                Token(Type.PLUS, "+", None, 1),
                ast.GroupingExpression(
                    ast.BinaryExpression(
                        ast.LiteralExpression(5),
                        Token(Type.STAR, "*", None, 1),
                        ast.UnaryExpression(
                            Token(Type.BANG, "!", None, 1), ast.LiteralExpression(True)
                        ),
                    )
                ),
            ),
            parse_expr("1 + 2 * 3 / -4 + (5 * !true)"),
        )

    def test_it_parses_ternary(self):
        self.assertEqual(
            ast.TernaryExpression(
                ast.LiteralExpression(1),
                Token(Type.QUESTION_MARK, "?", None, 1),
                ast.LiteralExpression(2),
                ast.LiteralExpression(3),
            ),
            parse_expr("1 ? 2 : 3"),
        )

        self.assertEqual(
            ast.TernaryExpression(
                ast.LiteralExpression(1),
                Token(Type.QUESTION_MARK, "?", None, 1),
                ast.LiteralExpression(2),
                ast.TernaryExpression(
                    ast.LiteralExpression(3),
                    Token(Type.QUESTION_MARK, "?", None, 1),
                    ast.LiteralExpression(4),
                    ast.LiteralExpression(5),
                ),
            ),
            parse_expr("1 ? 2 : 3 ? 4 : 5"),
        )

    def test_missing_closing_paren(self):
        (tokens, _) = Scanner("( 1").scan()
        (ast, errors) = Parser(tokens).parse()

        self.assertEqual(None, ast)
        self.assertEqual(
            [(Token(Type.EOF, "", None, 1), "Expected ')' after expression")], errors
        )

    def test_it_parses_statements(self):
        self.assertEqual(
            ast.Program(
                [
                    ast.ExpressionStatement(ast.LiteralExpression(1)),
                    ast.ExpressionStatement(ast.LiteralExpression(2)),
                ]
            ),
            parse("1;\n2;"),
        )

    def test_it_parses_print_statement(self):
        self.assertEqual(
            ast.Program([ast.PrintStatement([ast.LiteralExpression(1)])]),
            parse("print 1;"),
        )

        self.assertEqual(
            ast.Program(
                [
                    ast.PrintStatement(
                        [ast.LiteralExpression(1), ast.LiteralExpression(2)]
                    )
                ]
            ),
            parse("print 1, 2;"),
        )

    def test_it_parses_variable_declaration(self):
        self.assertEqual(
            ast.Program(
                [ast.VariableDeclaration(Token(Type.IDENTIFIER, "a", "a", 1), None)]
            ),
            parse("var a;"),
        )

    def test_it_parses_variable_declaration_with_initializer(self):
        self.assertEqual(
            ast.Program(
                [
                    ast.VariableDeclaration(
                        Token(Type.IDENTIFIER, "a", "a", 1), ast.LiteralExpression(4)
                    )
                ]
            ),
            parse("var a = 4;"),
        )

    def test_it_parser_variable_expression(self):
        self.assertEqual(
            ast.Program(
                [
                    ast.ExpressionStatement(
                        ast.VariableExpression(Token(Type.IDENTIFIER, "a", "a", 1))
                    )
                ]
            ),
            parse("a;"),
        )


def parse(code):
    (tokens, _) = Scanner(code).scan()
    (ast, errors) = Parser(tokens).parse()

    if len(errors) > 0:
        for e in errors:
            raise ValueError(e[1])

    return ast


def parse_expr(code):
    return parse(f"{code};").statements[0].expression
