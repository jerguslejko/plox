import unittest
from lib.parser import Parser, ParseError
from lib.scanner import Scanner
from lib.token import Token, Type
import lib.expression as E
import lib.statement as S


class ParserTest(unittest.TestCase):
    def test_it_parses_literals(self):
        self.assertEqual(
            E.LiteralExpression(1), parse_expr("1"),
        )

        self.assertEqual(
            E.LiteralExpression(1.2), parse_expr("1.2"),
        )

        self.assertEqual(
            E.LiteralExpression("hello"), parse_expr('"hello"'),
        )
        self.assertEqual(
            E.LiteralExpression("hello"), parse_expr("'hello'"),
        )

        self.assertEqual(
            E.LiteralExpression(True), parse_expr("true"),
        )

        self.assertEqual(
            E.LiteralExpression(False), parse_expr("false"),
        )

        self.assertEqual(
            E.LiteralExpression(None), parse_expr("nil"),
        )

        self.assertEqual(
            E.GroupingExpression(E.LiteralExpression(1)), parse_expr("(1)")
        )

    def test_it_parses_equality(self):
        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.EQUAL_EQUAL, "==", None, 1),
                E.LiteralExpression(1),
            ),
            parse_expr("1 == 1"),
        )

    def test_it_parses_comparison(self):
        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.LESS, "<", None, 1),
                E.LiteralExpression(1),
            ),
            parse_expr("1 < 1"),
        )

        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.LESS_EQUAL, "<=", None, 1),
                E.LiteralExpression(1),
            ),
            parse_expr("1 <= 1"),
        )

        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.GREATER, ">", None, 1),
                E.LiteralExpression(1),
            ),
            parse_expr("1 > 1"),
        )

        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.GREATER_EQUAL, ">=", None, 1),
                E.LiteralExpression(1),
            ),
            parse_expr("1 >= 1"),
        )

    def test_it_parses_addition(self):
        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.PLUS, "+", None, 1),
                E.LiteralExpression(1),
            ),
            parse_expr("1 + 1"),
        )

        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.MINUS, "-", None, 1),
                E.LiteralExpression(1),
            ),
            parse_expr("1 - 1"),
        )

    def test_it_parses_multiplicate(self):
        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.STAR, "*", None, 1),
                E.LiteralExpression(1),
            ),
            parse_expr("1 * 1"),
        )

        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.SLASH, "/", None, 1),
                E.LiteralExpression(1),
            ),
            parse_expr("1 / 1"),
        )

    def test_it_parses_unary(self):
        self.assertEqual(
            E.UnaryExpression(
                Token(Type.BANG, "!", None, 1), E.LiteralExpression(True),
            ),
            parse_expr("!true"),
        )

        self.assertEqual(
            E.UnaryExpression(
                Token(Type.MINUS, "-", None, 1), E.LiteralExpression(42),
            ),
            parse_expr("-42"),
        )

    def test_it_respects_operator_precedence(self):
        self.assertEqual(
            E.BinaryExpression(
                E.BinaryExpression(
                    E.LiteralExpression(1),
                    Token(Type.PLUS, "+", None, 1),
                    E.BinaryExpression(
                        E.BinaryExpression(
                            E.LiteralExpression(2),
                            Token(Type.STAR, "*", None, 1),
                            E.LiteralExpression(3),
                        ),
                        Token(Type.SLASH, "/", None, 1),
                        E.UnaryExpression(
                            Token(Type.MINUS, "-", None, 1), E.LiteralExpression(4),
                        ),
                    ),
                ),
                Token(Type.PLUS, "+", None, 1),
                E.GroupingExpression(
                    E.BinaryExpression(
                        E.LiteralExpression(5),
                        Token(Type.STAR, "*", None, 1),
                        E.UnaryExpression(
                            Token(Type.BANG, "!", None, 1), E.LiteralExpression(True)
                        ),
                    )
                ),
            ),
            parse_expr("1 + 2 * 3 / -4 + (5 * !true)"),
        )

    def test_it_parses_ternary(self):
        self.assertEqual(
            E.TernaryExpression(
                E.LiteralExpression(1),
                Token(Type.QUESTION_MARK, "?", None, 1),
                E.LiteralExpression(2),
                E.LiteralExpression(3),
            ),
            parse_expr("1 ? 2 : 3"),
        )

        self.assertEqual(
            E.TernaryExpression(
                E.LiteralExpression(1),
                Token(Type.QUESTION_MARK, "?", None, 1),
                E.LiteralExpression(2),
                E.TernaryExpression(
                    E.LiteralExpression(3),
                    Token(Type.QUESTION_MARK, "?", None, 1),
                    E.LiteralExpression(4),
                    E.LiteralExpression(5),
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
            S.Program(
                [
                    S.ExpressionStatement(E.LiteralExpression(1)),
                    S.ExpressionStatement(E.LiteralExpression(2)),
                ]
            ),
            parse("1;\n2;"),
        )

    def test_it_parses_print_statement(self):
        self.assertEqual(
            S.Program([S.PrintStatement(E.LiteralExpression(1))]), parse("print 1;")
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
