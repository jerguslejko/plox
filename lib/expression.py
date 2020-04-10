class Expression:
    def show(self):
        from lib.dot_printer import show_ast

        show_ast(self)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, vars(self))

    def __eq__(self, other):
        return isinstance(self, type(other)) and vars(self) == vars(other)


class TernaryExpression(Expression):
    def __init__(self, test, then, neht):
        self.test = test
        self.then = then
        self.neth = neht


class BinaryExpression(Expression):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class UnaryExpression(Expression):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right


class LiteralExpression(Expression):
    def __init__(self, value):
        self.value = value


class GroupingExpression(Expression):
    def __init__(self, expression):
        self.expression = expression
