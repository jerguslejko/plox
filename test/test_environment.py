import unittest
from lib.token import Token, Type
from lib.environment import Environment
from lib.error import UndefinedVariableError


class EnvironmentTest(unittest.TestCase):
    def test_it_stores_variables(self):
        env = Environment()

        env.put("foo", 1)

        self.assertEqual(1, env.get(var("foo")))

    def test_it_overrides_variables(self):
        env = Environment()

        env.put("foo", 1)
        env.put("foo", "bar")

        self.assertEqual("bar", env.get(var("foo")))

    def test_it_throws_when_accessing_undefined_variable(self):
        env = Environment()

        try:
            env.get(var("foo"))
        except UndefinedVariableError:
            pass
        else:
            self.fail("Expected exception")


def var(name):
    return Token(Type.IDENTIFIER, name, name, 1)
