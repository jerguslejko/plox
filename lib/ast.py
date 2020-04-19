class AST:
    def show(self):
        from lib.dot_printer import show_ast

        show_ast(self)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, vars(self))

    def __eq__(self, other):
        return isinstance(self, type(other)) and vars(self) == vars(other)


class Program(AST):
    def __init__(self, statements):
        self.statements = statements


class Statement(AST):
    pass


class Block(Statement):
    def __init__(self, statements):
        self.statements = statements


class ExpressionStatement(Statement):
    def __init__(self, expression):
        self.expression = expression


class PrintStatement(Statement):
    def __init__(self, expressions):
        self.expressions = expressions


class VariableDeclaration(Statement):
    def __init__(self, identifier, initializer):
        self.identifier = identifier
        self.initializer = initializer


class IfStatement(Statement):
    def __init__(self, test, then, neht):
        self.test = test
        self.then = then
        self.neht = neht


class Expression(AST):
    pass


class TernaryExpression(Expression):
    def __init__(self, test, operator, then, neht):
        self.test = test
        self.then = then
        self.neht = neht
        self.operator = operator


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


class VariableExpression(Expression):
    def __init__(self, variable):
        self.variable = variable


class AssignmentExpression(Expression):
    def __init__(self, left, token, right):
        self.left = left
        self.token = token
        self.right = right
