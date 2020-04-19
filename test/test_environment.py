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

    def test_it_gives_birth(self):
        env = Environment()
        child = env.child()

        self.assertEqual(env, child.parent)

    def test_it_allows_shadowing_by_child(self):
        env = Environment()
        env.define(identifier("foo"), 5)

        child = env.child()
        child.define(identifier("foo"), 6)

        self.assertEqual(5, env.get(identifier("foo")))
        self.assertEqual(6, child.get(identifier("foo")))

    def test_it_get_value_from_parent_if_not_present(self):
        env = Environment()
        env.define(identifier("foo"), 5)

        child = env.child()

        self.assertEqual(5, env.get(identifier("foo")))
        self.assertEqual(5, child.get(identifier("foo")))

    def test_it_proprages_assignment(self):
        env = Environment()
        env.define(identifier("foo"), 5)

        child = env.child()

        child.assign(identifier("foo"), 10)

        self.assertEqual(10, env.get(identifier("foo")))
        self.assertEqual(10, child.get(identifier("foo")))
