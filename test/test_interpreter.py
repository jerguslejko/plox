import unittest
from lib.parser import Parser, ParseError
from lib.scanner import Scanner
from lib.interpreter import Interpreter


class InterpreterTest(unittest.TestCase):
    def test_it_interprets_literals(self):
        self.assertEqual(1, run("1"))
        self.assertEqual(2.4, run("2.4"))
        self.assertEqual("hi", run('"hi"'))
        self.assertEqual(True, run("true"))
        self.assertEqual(False, run("false"))
        self.assertEqual(None, run("nil"))

    def test_it_interprets_grouping_expression(self):
        self.assertEqual(None, run("(nil)"))

    def test_it_interprets_unary_expressions(self):
        self.assertEqual(-2, run("-2"))
        self.assertEqual(2, run("--2"))
        self.assertEqual(True, run("!false"))
        self.assertEqual(False, run("!!false"))

    def test_it_interprets_binary_expressions(self):
        self.assertEqual(2, run("1 + 1"))
        self.assertEqual(-2, run("1 - 3"))
        self.assertEqual(8, run("1 * 8"))
        self.assertEqual(2, run("4 / 2"))
        self.assertEqual("foobar", run('"foo" + "bar"'))
        self.assertEqual("foo", run('"foobar" - "bar"'))
        self.assertEqual(False, run("1 > 2"))
        self.assertEqual(True, run("2 > 1"))
        self.assertEqual(True, run("1 < 2"))
        self.assertEqual(False, run("2 < 1"))
        self.assertEqual(True, run("1 <= 2"))
        self.assertEqual(True, run("2 <= 2"))
        self.assertEqual(False, run("3 <= 2"))
        self.assertEqual(False, run("1 >= 2"))
        self.assertEqual(True, run("2 >= 2"))
        self.assertEqual(True, run("3 >= 2"))
        self.assertEqual(True, run("1 == 1"))
        self.assertEqual(False, run("1 == 2"))
        self.assertEqual(False, run('1 == "1"'))
        self.assertEqual(True, run('"foo" == "foo"'))
        self.assertEqual(False, run('"foo" == "bar"'))
        self.assertEqual(True, run("nil == nil"))
        self.assertEqual(False, run("nil == 2"))
        self.assertEqual(False, run("1 != 1"))
        self.assertEqual(True, run("1 != 2"))
        self.assertEqual(True, run("true == true"))
        self.assertEqual(False, run("true == false"))

    def test_it_interprets_ternary_expressions(self):
        self.assertEqual(1, run("true ? 1 : 2"))
        self.assertEqual(2, run("false ? 1 : 2"))
        self.assertEqual(1, run("!false ? 1 : 2"))

    def test_it_validates_types(self):
        self.assertError(
            "Operand of (-) must be of type number, nil given", erun("-nil")
        )
        self.assertError(
            "Operand of (!) must be of type bool, number given", erun("!2.3")
        )
        self.assertError(
            "Operands of (+) must be of the same type. number and string given",
            erun("1 + 'foo'"),
        )
        self.assertError(
            "Operands of (+) must be of type number or string, bool given",
            erun("true + false"),
        )

    def assertError(self, message, result):
        (value, error) = result

        self.assertEqual(None, value)
        self.assertEqual(message, error.message)


def erun(code):
    (tokens, _) = Scanner(code).scan()
    (ast, _) = Parser(tokens).parse()
    return Interpreter(ast).interpret()


def run(code):
    (value, e) = erun(code)

    if e != None:
        raise e

    return value
