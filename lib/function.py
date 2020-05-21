import lib.interpreter
from lib.callable import Callable
from lib.environment import Environment


class Function(Callable):
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def identifier(self):
        return self.declaration.name

    def name(self):
        return self.identifier().lexeme

    def parameters(self):
        return self.declaration.parameters

    def body(self):
        return self.declaration.body

    def call(self, interpreter, arguments):
        env = Environment(self.closure)

        for (i, parameter) in enumerate(self.declaration.parameters):
            env.define(parameter, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, env)
        except lib.interpreter.Return as r:
            return r.value

        return None

    def arity(self):
        return len(self.declaration.parameters)


class AnonymousFunction(Function):
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def name(self):
        return "anonymous"
