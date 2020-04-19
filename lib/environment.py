from lib.error import UndefinedVariableError, RedeclaringVariableError


class Environment:
    def __init__(self):
        self.map = {}

    def define(self, var, value):
        if var.lexeme in self.map:
            raise RedeclaringVariableError(var)

        self.map[var.lexeme] = value

    def assign(self, var, value):
        if var.lexeme not in self.map:
            raise UndefinedVariableError(var)

        self.map[var.lexeme] = value

    def get(self, var):
        try:
            return self.map[var.lexeme]
        except KeyError:
            raise UndefinedVariableError(var)
