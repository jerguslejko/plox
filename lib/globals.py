from time import time, sleep
from lib.function import Callable


class ClockFunction(Callable):
    def name(self):
        return "clock"

    def arity(self):
        return 0

    def call(self, interpreter, arguments):
        interpreter.raise_return(time())


class SleepFunction(Callable):
    def name(self):
        return "sleep"

    def arity(self):
        return 1

    def call(self, interpreter, arguments):
        sleep(arguments[0])
