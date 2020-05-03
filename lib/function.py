from abc import ABC, abstractmethod
from lib.environment import Environment


class Callable(ABC):
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def call(self, interpreter, arguments):
        pass

    @abstractmethod
    def parameters(self):
        pass

    @abstractmethod
    def body(self):
        pass

    @abstractmethod
    def arity(self):
        pass

    @abstractmethod
    def to_str(self):
        pass


class Function(Callable):
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def name(self):
        return self.declaration.name

    def parameters(self):
        return self.declaration.parameters

    def body(self):
        return self.declaration.body

    def call(self, interpreter, arguments):
        env = Environment(self.closure)

        for (i, parameter) in enumerate(self.declaration.parameters):
            env.define(parameter, arguments[i])

        interpreter.execute_block(self.declaration.body, env)

    def arity(self):
        return len(self.declaration.parameters)

    def to_str(self):
        return "<fn %s>" % self.declaration.name.lexeme
