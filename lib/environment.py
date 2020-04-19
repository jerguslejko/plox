from lib.error import UndefinedVariableError


class Environment:
    def __init__(self):
        self.map = {}

    def put(self, name, value):
        self.map[name] = value

    def get(self, var):
        try:
            return self.map[var.lexeme]
        except KeyError:
            raise UndefinedVariableError(var)
