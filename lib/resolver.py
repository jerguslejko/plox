from lib import ast
from lib.error import ResolverError, CompileErrors
from enum import Enum, auto


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    METHOD = auto()
    INITIALIZER = auto()


class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()


class Resolver:
    def __init__(self, ast):
        self.ast = ast
        self.scopes = []
        self.bindings = {}
        self.errors = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    def run(self):
        self.resolve(self.ast)

        if self.errors:
            raise CompileErrors(self.errors)

        return self.bindings

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, token):
        if self.in_global_scope():
            return

        if token.lexeme in self.inner_scope():
            self.error(token, "Variable [%s] is already defined" % token.lexeme)

        self.inner_scope()[token.lexeme] = False

    def define(self, token):
        if self.in_global_scope():
            return

        self.inner_scope()[token.lexeme] = True

    def resolve_block(self, node):
        self.begin_scope()

        for statement in node.statements:
            self.resolve(statement)

        self.end_scope()

    def resolve_variable_declaration(self, node):
        self.declare(node.identifier)

        if node.initializer:
            self.resolve(node.initializer)

        self.define(node.identifier)

    def resolve_local(self, node, name):
        for i in range(len(self.scopes) - 1, 0 - 1, -1):
            scope = self.scopes[i]
            if name in scope:
                self.add_binding(node, len(self.scopes) - 1 - i)
                return

        # otherwise it's global

    def resolve_function(self, node, declaration):
        self.declare(node.name)
        self.define(node.name)
        self.resolve_anonymous_function(node, declaration)

    def resolve_anonymous_function(self, node, declaration):
        enclosing_function = self.current_function
        self.current_function = declaration
        self.begin_scope()

        for parameter in node.parameters:
            self.declare(parameter)
            self.define(parameter)

        if isinstance(node, ast.LambdaExpression):
            self.resolve(node.expression)
        else:
            for statement in node.body.statements:
                self.resolve(statement)

        self.end_scope()
        self.current_function = enclosing_function

    def resolve_class(self, node):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS

        self.declare(node.name)

        if node.super:
            self.current_class = ClassType.SUBCLASS

            if node.name.lexeme == node.super.variable.lexeme:
                self.error(node.super.variable, "A class cannot inherit from itself")

            self.resolve(node.super)

            self.begin_scope()
            self.inner_scope()["super"] = True

        self.begin_scope()
        self.inner_scope()["this"] = True

        for method in node.methods:
            declaration = FunctionType.METHOD

            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER

            self.resolve_function(method, declaration)

        self.define(node.name)

        if node.super:
            self.end_scope()

        self.end_scope()

        self.current_class = enclosing_class

    def resolve(self, node):
        if isinstance(node, ast.Program):
            for statement in node.statements:
                self.resolve(statement)
            return

        if isinstance(node, ast.Block):
            return self.resolve_block(node)

        if isinstance(node, ast.ClassDeclaration):
            return self.resolve_class(node)

        if isinstance(node, ast.FunctionDeclaration):
            return self.resolve_function(node, FunctionType.FUNCTION)

        if isinstance(node, ast.VariableDeclaration):
            return self.resolve_variable_declaration(node)

        if isinstance(node, ast.PrintStatement):
            for expression in node.expressions:
                self.resolve(expression)

            return

        if isinstance(node, ast.IfStatement):
            self.resolve(node.test)
            self.resolve(node.then)
            if node.neht:
                self.resolve(node.neht)
            return

        if isinstance(node, ast.WhileStatement):
            self.resolve(node.test)
            self.resolve(node.body)
            return

        if isinstance(node, ast.ReturnStatement):
            if self.current_function == FunctionType.NONE:
                self.error(node.token, "Cannot return from top-level code")

            if self.current_function == FunctionType.INITIALIZER:
                self.error(node.token, "Cannot return a value from an initializer")

            self.resolve(node.expression)
            return

        if isinstance(node, ast.BinaryExpression):
            self.resolve(node.left)
            self.resolve(node.right)
            return

        if isinstance(node, ast.GroupingExpression):
            self.resolve(node.expression)
            return

        if isinstance(node, ast.LogicalExpression):
            self.resolve(node.left)
            self.resolve(node.right)
            return

        if isinstance(node, ast.ExpressionStatement):
            return self.resolve(node.expression)

        if isinstance(node, ast.VariableExpression):
            if self.variable_access_inside_own_initializer(node):
                self.error(
                    node.variable,
                    "Variable [%s] accessed inside its own initializer"
                    % node.variable.lexeme,
                )

            self.resolve_local(node, node.variable.lexeme)
            return

        if isinstance(node, ast.CallExpression):
            self.resolve(node.callee)

            for argument in node.arguments:
                self.resolve(argument)

            return

        if isinstance(node, ast.GetExpression):
            self.resolve(node.object)
            return

        if isinstance(node, ast.SetExpression):
            self.resolve(node.value)
            self.resolve(node.object)
            return

        if isinstance(node, ast.FunctionExpression):
            self.resolve_anonymous_function(node, FunctionType.FUNCTION)
            return

        if isinstance(node, ast.LambdaExpression):
            self.resolve_anonymous_function(node, FunctionType.FUNCTION)
            return

        if isinstance(node, ast.AssignmentExpression):
            self.resolve(node.right)
            self.resolve_local(node, node.left.lexeme)
            return

        if isinstance(node, ast.TernaryExpression):
            self.resolve(node.test)
            self.resolve(node.then)
            if node.neht:
                self.resolve(node.neht)
            return

        if isinstance(node, ast.LiteralExpression):
            return

        if isinstance(node, ast.UnaryExpression):
            self.resolve(node.right)
            return

        if isinstance(node, ast.ThisExpression):
            if self.current_class == ClassType.NONE:
                self.error(node, "Cannot use 'this' outside of a class")

            self.resolve_local(node, node.token.lexeme)
            return

        if isinstance(node, ast.SuperExpression):
            if self.current_class == ClassType.NONE:
                self.error(node, "Cannot use 'super' outside of a class")
            elif self.current_class != ClassType.SUBCLASS:
                self.error(node, "Cannot use 'super' in a class with no superclass")

            self.resolve_local(node, node.keyword.lexeme)
            return

        raise ValueError("[resolver] unsupported ast node [%s]" % node.__class__)

    def in_global_scope(self):
        return len(self.scopes) == 0

    def inner_scope(self):
        return self.scopes[-1]

    def variable_access_inside_own_initializer(self, node):
        if self.in_global_scope():
            return False

        scope = self.inner_scope()
        variable = node.variable.lexeme

        if variable not in scope:
            return False

        return scope[variable] == False

    def add_binding(self, node, depth):
        self.bindings[node] = depth

    def error(self, token, message):
        self.errors.append(ResolverError(token, message))
