import lib.interpreter
from lib.callable import Callable
from lib.environment import Environment
from lib.token import identifier


class Function(Callable):
    def __init__(self, declaration, closure, isInitializer):
        self.declaration = declaration
        self.closure = closure
        self.isInitializer = isInitializer

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

        if self.isInitializer:
            return self.closure.get_at(0, identifier("this"))

        return None

    def arity(self):
        return len(self.declaration.parameters)

    def bind(self, this):
        env = self.closure.child()
        env.define(identifier("this"), this)
        return Function(self.declaration, env, self.isInitializer)


class AnonymousFunction(Function):
    def name(self):
        return "anonymous"
