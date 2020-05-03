from lib.error import (
    UndefinedVariableError,
    RedeclaringVariableError,
    UninitializedVariableError,
)


class EmptyValue:
    pass


class Environment:
    def __init__(self, parent=None):
        self.map = {}
        self.parent = parent

    def define(self, var, value=EmptyValue()):
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

        value = self.map[var.lexeme]

        if isinstance(value, EmptyValue):
            raise UninitializedVariableError(var)

        return value

    def child(self):
        return Environment(self)

    def get_at(self, depth, name):
        return self.ancestor(depth).get(name)

    def assign_at(self, depth, name, value):
        self.ancestor(depth).assign(name, value)

    def ancestor(self, depth):
        ancestor = self

        for i in range(0, depth):
            if ancestor.parent is None:
                raise ValueError("E_TOO_DEEP")

            ancestor = ancestor.parent

        return ancestor
