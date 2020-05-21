from abc import ABC, abstractmethod


class Callable(ABC):
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def call(self, interpreter, arguments):
        pass

    @abstractmethod
    def arity(self):
        pass

    def to_str(self):
        return "<fun %s>" % self.name()
