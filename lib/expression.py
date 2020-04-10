class Expression:
    pass


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
