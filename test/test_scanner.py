import unittest
from lib.scanner import Scanner
from lib.token import Token, Type


class ScannerTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_it_includes_eof(self):
        (tokens, _) = Scanner("").scan()

        self.assertEqual([
            Token(Type.EOF, "", None, 1),
        ], tokens)

    def test_it_parses_single_char_tokens(self):
        self.assertEqual([
            Token(Type.LEFT_PAREN, "(", None, 1),
            Token(Type.RIGHT_PAREN, ")", None, 1),
            Token(Type.LEFT_BRACE, "{", None, 1),
            Token(Type.RIGHT_BRACE, "}", None, 1),
            Token(Type.COMMA, ",", None, 1),
            Token(Type.DOT, ".", None, 1),
            Token(Type.MINUS, "-", None, 1),
            Token(Type.PLUS, "+", None, 1),
            Token(Type.SEMICOLON, ";", None, 1),
            Token(Type.STAR, "*", None, 1),
            Token(Type.SLASH, "/", None, 1),
            Token(Type.BANG, "!", None, 1),
            Token(Type.EQUAL, "=", None, 1),
            Token(Type.LESS, "<", None, 1),
            Token(Type.GREATER, ">", None, 1),
            Token(Type.QUESTION_MARK, "?", None, 1),
            Token(Type.COLON, ":", None, 1),
        ], scan("( ) { } , . - + ; * / ! = < > ? :"))

    def test_it_parses_double_char_tokens(self):
        self.assertEqual([
            Token(Type.BANG_EQUAL, "!=", None, 1),
            Token(Type.EQUAL_EQUAL, "==", None, 1),
            Token(Type.LESS_EQUAL, "<=", None, 1),
            Token(Type.GREATER_EQUAL, ">=", None, 1),
        ], scan("!= == <= >="))

    def test_it_handles_multiline_source(self):
        self.assertEqual([
            Token(Type.EQUAL, "=", None, 1),
            Token(Type.BANG_EQUAL, "!=", None, 2),
            Token(Type.PLUS, "+", None, 3),
        ], scan("=\n!=\n+"))

    def test_it_parses_strings(self):
        self.assertEqual([
            Token(Type.STRING, '"hello"', "hello", 1),
        ], scan('"hello"'))

    def test_it_parses_numbers(self):
        self.assertEqual([
            Token(Type.NUMBER, "42", 42, 1),
            Token(Type.NUMBER, "69.96", 69.96, 1),
        ], scan("42 69.96"))

    def test_it_parses_identifiers(self):
        self.assertEqual([
            Token(Type.IDENTIFIER, "foo", "foo", 1),
            Token(Type.IDENTIFIER, "bar", "bar", 1),
        ], scan("foo bar"))

    def test_it_parses_keywords(self):
        self.assertEqual([
            Token(Type.AND, "and", None, 1),
            Token(Type.CLASS, "class", None, 1),
            Token(Type.ELSE, "else", None, 1),
            Token(Type.FALSE, "false", None, 1),
            Token(Type.FOR, "for", None, 1),
            Token(Type.FUN, "fun", None, 1),
            Token(Type.IF, "if", None, 1),
            Token(Type.NIL, "nil", None, 1),
            Token(Type.OR, "or", None, 1),
            Token(Type.PRINT, "print", None, 1),
            Token(Type.RETURN, "return", None, 1),
            Token(Type.SUPER, "super", None, 1),
            Token(Type.THIS, "this", None, 1),
            Token(Type.TRUE, "true", None, 1),
            Token(Type.VAR, "var", None, 1),
            Token(Type.WHILE, "while", None, 1),
        ], scan("and class else false for fun if nil or print return super this true var while"))

    def test_it_reports_unterminated_string(self):
        (tokens, errors) = Scanner('"hello').scan()

        self.assertEqual([(1, 'Unterminated string')], errors)
        self.assertEqual([], tokens[:-1])

    def test_it_reports_unknown_char(self):
        (tokens, errors) = Scanner('@').scan()

        self.assertEqual([], tokens[:-1])
        self.assertEqual([(1, 'Unrecognized character [@]')], errors)


def scan(code):
    return Scanner(code).scan()[0][:-1]
