import unittest
from lib.token import Token, Type, identifier
from lib.environment import Environment
from lib.error import UndefinedVariableError, RedeclaringVariableError


class EnvironmentTest(unittest.TestCase):
    def test_it_stores_variables(self):
        env = Environment()

        env.define(identifier("foo"), 1)

        self.assertEqual(1, env.get(identifier("foo")))

    def test_it_throws_when_redefining_variable(self):
        env = Environment()

        env.define(identifier("foo"), 1)

        try:
            env.define(identifier("foo"), "bar")
        except RedeclaringVariableError:
            pass
        else:
            self.fail("Expected exception")

    def test_it_throws_when_accessing_undefined_variable(self):
        env = Environment()

        try:
            env.get(identifier("foo"))
        except UndefinedVariableError:
            pass
        else:
            self.fail("Expected exception")

    def test_it_allows_to_reassign_variable(self):
        env = Environment()

        env.define(identifier("foo"), 1)
        env.assign(identifier("foo"), 5)

        self.assertEqual(5, env.get(identifier("foo")))

    def test_it_throws_when_reassigning_non_existing_variable(self):
        env = Environment()

        try:
            env.assign(identifier("foo"), 5)
        except UndefinedVariableError:
            pass
        else:
            self.fail("Expected exception")
