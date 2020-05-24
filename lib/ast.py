import black


class AST:
    def __hash__(self):
        return id(self)

    def __repr__(self):
        ast = "%s(%s)" % (self.__class__.__name__, vars(self),)

        return black.format_str(ast, mode=black.FileMode())

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


class ClassDeclaration(Statement):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods


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


class FunctionDeclaration(Statement):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body


class IfStatement(Statement):
    def __init__(self, test, then, neht):
        self.test = test
        self.then = then
        self.neht = neht


class WhileStatement(Statement):
    def __init__(self, token, test, body):
        self.token = token
        self.test = test
        self.body = body


class ReturnStatement(Statement):
    def __init__(self, expression, token):
        self.expression = expression
        self.token = token


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


class LogicalExpression(Expression):
    def __init__(self, left, token, right):
        self.left = left
        self.token = token
        self.right = right


class CallExpression(Expression):
    def __init__(self, callee, token, arguments):
        self.callee = callee
        self.token = token
        self.arguments = arguments


class GetExpression(Expression):
    def __init__(self, object, name):
        self.object = object
        self.name = name


class SetExpression(Expression):
    def __init__(self, object, name, value):
        self.object = object
        self.name = name
        self.value = value


class FunctionExpression(Expression):
    def __init__(self, parameters, body):
        self.parameters = parameters
        self.body = body


class LambdaExpression(Expression):
    def __init__(self, parameters, arrow, expression):
        self.parameters = parameters
        self.arrow = arrow
        self.expression = expression


class ThisExpression(Expression):
    def __init__(self, token):
        self.token = token
