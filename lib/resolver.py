from lib import ast
from lib.error import ResolverError, CompileErrors


class Resolver:
    def __init__(self, ast):
        self.ast = ast
        self.scopes = []
        self.bindings = {}
        self.errors = []

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

    def resolve_function(self, node):
        self.declare(node.name)
        self.define(node.name)

        self.begin_scope()

        for parameter in node.parameters:
            self.declare(parameter)
            self.define(parameter)

        for statement in node.body.statements:
            self.resolve(statement)

        self.end_scope()

    def resolve(self, node):
        if isinstance(node, ast.Program):
            for statement in node.statements:
                self.resolve(statement)
            return

        if isinstance(node, ast.Block):
            return self.resolve_block(node)

        if isinstance(node, ast.FunctionDeclaration):
            return self.resolve_function(node)

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

        if isinstance(node, ast.FunctionExpression):
            self.begin_scope()

            for parameter in node.parameters:
                self.declare(parameter)
                self.define(parameter)

            for statement in node.body.statements:
                self.resolve(statement)

            self.end_scope()

            return

        if isinstance(node, ast.LambdaExpression):
            self.begin_scope()

            for parameter in node.parameters:
                self.declare(parameter)
                self.define(parameter)

            self.resolve(node.expression)

            self.end_scope()

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
