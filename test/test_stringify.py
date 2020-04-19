import unittest
from lib.stringify import stringify, stringify_type, stringify_types


class StringifyTest(unittest.TestCase):
    def test_it_stringifies_values(self):
        self.assertEqual("1", stringify(1))
        self.assertEqual("1.3", stringify(1.3))
        self.assertEqual("foo", stringify("foo"))
        self.assertEqual("nil", stringify(None))
        self.assertEqual("true", stringify(True))
        self.assertEqual("false", stringify(False))

    def test_it_stringifies_types(self):
        self.assertEqual("string", stringify_type(str))
        self.assertEqual("number", stringify_type(int))
        self.assertEqual("number", stringify_type(float))
        self.assertEqual("bool", stringify_type(bool))
        self.assertEqual("nil", stringify_type(None.__class__))

    def test_it_stringifies_list_of_types(self):
        self.assertEqual(["number", "string"], stringify_types([float, str]))

    def test_it_filters_out_duplicates(self):
        self.assertEqual(["number"], stringify_types([int, float]))
