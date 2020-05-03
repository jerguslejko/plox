from lib.token import Token, Type
from lib.error import ScanError


class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.errors = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan(self):
        while not self.at_end():
            self.start = self.current
            self.scan_single()

        self.tokens.append(Token(Type.EOF, "", None, self.line))

        return (self.tokens, self.errors)

    def scan_single(self):
        c = self.advance()

        if c == "(":
            self.add_token(Type.LEFT_PAREN)
        elif c == ")":
            self.add_token(Type.RIGHT_PAREN)
        elif c == "{":
            self.add_token(Type.LEFT_BRACE)
        elif c == "}":
            self.add_token(Type.RIGHT_BRACE)
        elif c == ",":
            self.add_token(Type.COMMA)
        elif c == ".":
            self.add_token(Type.DOT)
        elif c == "+":
            self.add_token(Type.PLUS)
        elif c == ";":
            self.add_token(Type.SEMICOLON)
        elif c == "*":
            self.add_token(Type.STAR)
        elif c == "/":
            self.add_token(Type.SLASH)
        elif c == "?":
            self.add_token(Type.QUESTION_MARK)
        elif c == ":":
            self.add_token(Type.COLON)
        elif c == "\\":
            self.add_token(Type.BACKSLASH)
        elif c == "!":
            self.add_token(Type.BANG_EQUAL if self.match("=") else Type.BANG)
        elif c == "=":
            self.add_token(Type.EQUAL_EQUAL if self.match("=") else Type.EQUAL)
        elif c == "<":
            self.add_token(Type.LESS_EQUAL if self.match("=") else Type.LESS)
        elif c == ">":
            self.add_token(Type.GREATER_EQUAL if self.match("=") else Type.GREATER)
        elif c == "-":
            self.add_token(Type.ARROW) if self.match(">") else self.add_token(
                Type.MINUS
            )
        elif c == '"':
            self.string('"')
        elif c == "'":
            self.string("'")
        elif c == " " or c == "\r" or c == "\t":
            pass
        elif c == "\n":
            self.line += 1
        elif self.is_digit(c):
            self.number()
        elif self.is_alpha(c):
            self.identifier()
        else:
            self.error("Unrecognized character [%s]" % c)

    def string(self, quote):
        while self.peek() != quote and not self.at_end():
            if self.peek() == "\n":
                self.line += 1

            self.advance()

        if self.at_end():
            self.error("Unterminated string")
            return

        self.advance()

        self.add_token(Type.STRING, self.source[self.start + 1 : self.current - 1])

    def number(self):
        is_float = False

        while self.is_digit(self.peek()):
            self.advance()

        if self.peek() == "." and self.is_digit(self.peek_next()):
            is_float = True
            self.advance()

            while self.is_digit(self.peek()):
                self.advance()

        str_value = self.source[self.start : self.current]
        value = float(str_value) if is_float else int(str_value)

        self.add_token(Type.NUMBER, value)

    def identifier(self):
        while self.is_alpha_numeric(self.peek()):
            self.advance()

        keyword = self.source[self.start : self.current]

        keywords = {
            "and": Type.AND,
            "or": Type.OR,
            "class": Type.CLASS,
            "if": Type.IF,
            "else": Type.ELSE,
            "true": Type.TRUE,
            "false": Type.FALSE,
            "for": Type.FOR,
            "fun": Type.FUN,
            "nil": Type.NIL,
            "print": Type.PRINT,  # TODO: remove this
            "while": Type.WHILE,
            "this": Type.THIS,
            "var": Type.VAR,
            "super": Type.SUPER,
            "return": Type.RETURN,
        }

        if keyword in keywords:
            self.add_token(keywords.get(keyword))
        else:
            self.add_token(Type.IDENTIFIER, keyword)

    def is_digit(self, n):
        return n >= "0" and n <= "9"

    def is_alpha(self, c):
        return (c >= "a" and c <= "z") or (c >= "A" and c <= "Z") or (c == "_")

    def is_alpha_numeric(self, c):
        return self.is_digit(c) or self.is_alpha(c)

    def advance(self):
        self.current += 1
        return self.source[self.current - 1]

    def at_end(self):
        return self.current >= len(self.source)

    def peek(self):
        if self.at_end():
            return "\0"

        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return "\0"

        return self.source[self.current + 1]

    def match(self, expected):
        if self.at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.advance()
        return True

    def add_token(self, type, literal=None):
        self.tokens.append(
            Token(type, self.source[self.start : self.current], literal, self.line)
        )

    def error(self, message):
        self.errors.append(ScanError(self.line, message))
