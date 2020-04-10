import unittest
from lib.parser import Parser, ParseError
from lib.scanner import Scanner
from lib.token import Token, Type
import lib.expression as E


class ParserTest(unittest.TestCase):
    def test_it_parses_literals(self):
        self.assertEqual(
            E.LiteralExpression(1),
            parse("1"),
        )

        self.assertEqual(
            E.LiteralExpression(1.2),
            parse("1.2"),
        )

        self.assertEqual(
            E.LiteralExpression("hello"),
            parse('"hello"'),
        )

        self.assertEqual(
            E.LiteralExpression(True),
            parse('true'),
        )

        self.assertEqual(
            E.LiteralExpression(False),
            parse('false'),
        )

        self.assertEqual(
            E.LiteralExpression(None),
            parse('nil'),
        )

        self.assertEqual(
            E.GroupingExpression(
                E.LiteralExpression(1)
            ),
            parse('(1)')
        )

    def test_it_parses_equality(self):
        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.EQUAL_EQUAL, '==', None, 1),
                E.LiteralExpression(1),
            ),
            parse("1 == 1")
        )

    def test_it_parses_comparison(self):
        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.LESS, '<', None, 1),
                E.LiteralExpression(1),
            ),
            parse("1 < 1")
        )

        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.LESS_EQUAL, '<=', None, 1),
                E.LiteralExpression(1),
            ),
            parse("1 <= 1")
        )

        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.GREATER, '>', None, 1),
                E.LiteralExpression(1),
            ),
            parse("1 > 1")
        )

        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.GREATER_EQUAL, '>=', None, 1),
                E.LiteralExpression(1),
            ),
            parse("1 >= 1")
        )

    def test_it_parses_addition(self):
        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.PLUS, '+', None, 1),
                E.LiteralExpression(1),
            ),
            parse("1 + 1")
        )

        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.MINUS, '-', None, 1),
                E.LiteralExpression(1),
            ),
            parse("1 - 1")
        )

    def test_it_parses_multiplicate(self):
        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.STAR, '*', None, 1),
                E.LiteralExpression(1),
            ),
            parse("1 * 1")
        )

        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.SLASH, '/', None, 1),
                E.LiteralExpression(1),
            ),
            parse("1 / 1")
        )

    def test_it_parses_unary(self):
        self.assertEqual(
            E.UnaryExpression(
                Token(Type.BANG, '!', None, 1),
                E.LiteralExpression(True),
            ),
            parse("!true")
        )

        self.assertEqual(
            E.UnaryExpression(
                Token(Type.MINUS, '-', None, 1),
                E.LiteralExpression(42),
            ),
            parse("-42")
        )

    def test_it_respects_operator_precedence(self):
        self.assertEqual(
            E.BinaryExpression(
                E.BinaryExpression(
                    E.LiteralExpression(1),
                    Token(Type.PLUS, '+', None, 1),
                    E.BinaryExpression(
                        E.BinaryExpression(
                            E.LiteralExpression(2),
                            Token(Type.STAR, '*', None, 1),
                            E.LiteralExpression(3),
                        ),
                        Token(Type.SLASH, '/', None, 1),
                        E.UnaryExpression(
                            Token(Type.MINUS, '-', None, 1),
                            E.LiteralExpression(4),
                        )
                    )
                ),
                Token(Type.PLUS, '+', None, 1),
                E.GroupingExpression(
                    E.BinaryExpression(
                        E.LiteralExpression(5),
                        Token(Type.STAR, '*', None, 1),
                        E.UnaryExpression(
                            Token(Type.BANG, '!', None, 1),
                            E.LiteralExpression(True)
                        )
                    )
                )
            ),
            parse("1 + 2 * 3 / -4 + (5 * !true)")
        )

    def test_it_parses_comma_expressions(self):
        self.assertEqual(
            E.BinaryExpression(
                E.LiteralExpression(1),
                Token(Type.COMMA, ',', None, 1),
                E.LiteralExpression(2),
            ),
            parse("1,2")
        )

    def test_it_parses_ternary(self):
        self.assertEqual(
            E.TernaryExpression(
                E.LiteralExpression(1),
                E.LiteralExpression(2),
                E.LiteralExpression(3),
            ),
            parse("1 ? 2 : 3")
        )

        self.assertEqual(
            E.TernaryExpression(
                E.LiteralExpression(1),
                E.LiteralExpression(2),
                E.TernaryExpression(
                    E.LiteralExpression(3),
                    E.LiteralExpression(4),
                    E.LiteralExpression(5),
                ),
            ),
            parse("1 ? 2 : 3 ? 4 : 5")
        )

    def test_it_throws_on_unconsumed_tokens(self):
        try:
            parse("1 +")
        except ParseError:
            return

        self.fail("Expected parse error")

    def test_missing_closing_paren(self):
        try:
            parse("( 1")
        except ParseError:
            return

        self.fail("Expected parse error")


def parse(code):
    tokens = Scanner(code).scan()

    return Parser(tokens).parse()
