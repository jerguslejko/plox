import unittest
from math import floor, ceil


class TestCase(unittest.TestCase):
    maxDiff = None

    def assertAstMatches(self, expected, actual, visual=True):
        if visual:
            if expected != actual:
                self.dumpAst("Expected AST", expected)
                self.dumpAst("Actual AST", actual)

                self.assertEqual(str(expected), str(actual))

                self.fail("ASTs don't match.")
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
