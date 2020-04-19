from lib.error import UndefinedVariableError, RedeclaringVariableError


class Environment:
    def __init__(self, parent=None):
        self.map = {}
        self.parent = parent

    def define(self, var, value):
        if var.lexeme in self.map:
            raise RedeclaringVariableError(var)

        self.map[var.lexeme] = value

    def assign(self, var, value):
        if var.lexeme not in self.map:
            if self.parent:
                return self.parent.assign(var, value)

            raise UndefinedVariableError(var)

        self.map[var.lexeme] = value

    def get(self, var):
        if var.lexeme not in self.map:
            if self.parent:
                return self.parent.get(var)

            raise UndefinedVariableError(var)

        return self.map[var.lexeme]

    def child(self):
        return Environment(self)
