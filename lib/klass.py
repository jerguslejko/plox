from lib.callable import Callable
from lib.error import RuntimeError


class Instance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def get(self, name):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method:
            return method.bind(self)

        raise RuntimeError(name, "Undefined property [%s]" % name.lexeme)

    def set(self, name, value):
        self.fields[name.lexeme] = value

    def to_str(self):
        return "<instance %s>" % self.klass.name


class Klass(Callable):
    def __init__(self, name, super, methods):
        self.name = name
        self.super = super
        self.methods = methods

    def arity(self):
        initializer = self.find_method("init")

        return initializer.arity() if initializer else 0

    def call(self, interpreter, arguments):
        instance = Instance(self)

        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)

        return instance

    def name(self):
        return self.name

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]

        if self.super:
            return self.super.find_method(name)

        return None

    def to_str(self):
        return "<class %s>" % self.name
