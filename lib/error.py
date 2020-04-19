from lib.stringify import stringify, stringify_type, stringify_types


class RuntimeError(BaseException):
    def __init__(self, token, message):
        self.token = token
        self.message = message

    def __str__(self):
        return "runtime error on line %d: %s" % (self.token.line, self.message)

    def __eq__(self, other):
        return self.token == other.token and self.message == other.message


class CompileError(BaseException):
    pass


class ScanError(CompileError):
    def __init__(self, line, message):
        self.line = line
        self.message = message

    def __str__(self):
        return "scan error on line %d: %s" % (self.line, self.message)

    def __eq__(self, other):
        return self.line == other.line and self.message == other.message


class ParseError(CompileError):
    def __init__(self, token, message):
        self.token = token
        self.message = message

    def __str__(self):
        return "parse error on line %d: %s" % (self.token.line, self.message)

    def __eq__(self, other):
        return self.token == other.token and self.message == other.message


class UndefinedVariableError(RuntimeError):
    def __init__(self, token):
        self.token = token
        self.message = "Variable [%s] is not defined" % token.lexeme


class RedeclaringVariableError(RuntimeError):
    def __init__(self, token):
        self.token = token
        self.message = "Variable [%s] is already defined" % token.lexeme


class TypeError(RuntimeError):
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
