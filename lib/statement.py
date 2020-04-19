class Program:
    def __init__(self, statements):
        self.statements = statements

    def show(self):
        from lib.dot_printer import show_ast

        show_ast(self)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, vars(self))

    def __eq__(self, other):
        return isinstance(self, type(other)) and vars(self) == vars(other)


class Statement:
    def show(self):
        from lib.dot_printer import show_ast

        show_ast(self)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, vars(self))

    def __eq__(self, other):
        return isinstance(self, type(other)) and vars(self) == vars(other)


class ExpressionStatement(Statement):
    def __init__(self, expression):
        self.expression = expression


class PrintStatement(Statement):
    def __init__(self, expression):
        self.expression = expression
