import unittest
from lib.scanner import Scanner


class ScannerTest(unittest.TestCase):
    def test_it_includes_eof(self):
        self.assertEqual([], Scanner("").scan())
