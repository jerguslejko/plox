import unittest
from math import floor, ceil


class TestCase(unittest.TestCase):
    def assertAstMatches(self, expected, actual, visual=True):
        if visual:
            if expected != actual:
                self.dumpAst("Expected AST", expected)
                self.dumpAst("Actual AST", actual)
                self.fail("shit ain't good")
        else:
            self.assertEqual(expected, actual)

    def dumpAst(self, heading, ast):
        print("")
        print("**************************************************")
        print(
            "* %s%s%s *"
            % (
                " " * floor(23 - len(heading) / 2),
                heading,
                " " * ceil(23 - len(heading) / 2),
            )
        )
        print("**************************************************")
        print("")
        ast.show()
        print("")
