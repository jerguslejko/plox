import sys
import os
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, "../lib")

if path not in sys.path:
    sys.path.append(path)


class TestCase(unittest.TestCase):
    maxDiff = None

    def assertAstMatches(self, expected, actual):
        # comparing large ASTs is faster
        # than comparing large strings
        if expected != actual:
            self.assertEqual(str(expected), str(actual))
