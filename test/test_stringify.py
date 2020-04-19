import unittest
from lib.stringify import stringify_type, stringify_types


class StringifyTest(unittest.TestCase):
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
