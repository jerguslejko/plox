import unittest
from lib.parser import Parser, ParseError
from lib.scanner import Scanner
from lib.interpreter import Interpreter, TypeError
from lib.ast import Program, VariableExpression
from lib.token import identifier


class InterpreterTest(unittest.TestCase):
    def test_it_interprets_literals(self):
        self.assertEqual(1, run_expr("1"))
        self.assertEqual(2.4, run_expr("2.4"))
        self.assertEqual("hi", run_expr('"hi"'))
        self.assertEqual(True, run_expr("true"))
        self.assertEqual(False, run_expr("false"))
        self.assertEqual(None, run_expr("nil"))

    def test_it_interprets_grouping_expression(self):
        self.assertEqual(None, run_expr("(nil)"))

    def test_it_interprets_unary_expressions(self):
        self.assertEqual(-2, run_expr("-2"))
        self.assertEqual(2, run_expr("--2"))
        self.assertEqual(True, run_expr("!false"))
        self.assertEqual(False, run_expr("!!false"))

    def test_it_interprets_binary_expressions(self):
        self.assertEqual(2, run_expr("1 + 1"))
        self.assertEqual(-2, run_expr("1 - 3"))
        self.assertEqual(8, run_expr("1 * 8"))
        self.assertEqual(2, run_expr("4 / 2"))
        self.assertEqual("foobar", run_expr('"foo" + "bar"'))
        self.assertEqual("foo", run_expr('"foobar" - "bar"'))
        self.assertEqual(False, run_expr("1 > 2"))
        self.assertEqual(True, run_expr("2 > 1"))
        self.assertEqual(True, run_expr("1 < 2"))
        self.assertEqual(False, run_expr("2 < 1"))
        self.assertEqual(True, run_expr("1 <= 2"))
        self.assertEqual(True, run_expr("2 <= 2"))
        self.assertEqual(False, run_expr("3 <= 2"))
        self.assertEqual(False, run_expr("1 >= 2"))
        self.assertEqual(True, run_expr("2 >= 2"))
        self.assertEqual(True, run_expr("3 >= 2"))
        self.assertEqual(True, run_expr("1 == 1"))
        self.assertEqual(False, run_expr("1 == 2"))
        self.assertEqual(False, run_expr('1 == "1"'))
        self.assertEqual(True, run_expr('"foo" == "foo"'))
        self.assertEqual(False, run_expr('"foo" == "bar"'))
        self.assertEqual(True, run_expr("nil == nil"))
        self.assertEqual(False, run_expr("nil == 2"))
        self.assertEqual(False, run_expr("1 != 1"))
        self.assertEqual(True, run_expr("1 != 2"))
        self.assertEqual(True, run_expr("true == true"))
        self.assertEqual(False, run_expr("true == false"))

    def test_it_interprets_ternary_expressions(self):
        self.assertEqual(1, run_expr("true ? 1 : 2"))
        self.assertEqual(2, run_expr("false ? 1 : 2"))
        self.assertEqual(1, run_expr("!false ? 1 : 2"))

    def test_it_validates_types(self):
        self.assertError(
            "Operand of (-) must be of type number, nil given", lambda: run_expr("-nil")
        )

        self.assertError(
            "Operand of (!) must be of type bool, number given",
            lambda: run_expr("!2.3"),
        )
        self.assertError(
            "Operands of (+) must be of the same type. number and string given",
            lambda: run_expr("1 + 'foo'"),
        )
        self.assertError(
            "Operands of (+) must be of type number or string, bool given",
            lambda: run_expr("true + false"),
        )

    def test_it_interprets_variable_declarations_and_expressions(self):
        (tokens, _) = Scanner("var a = 4;").scan()
        (ast, _) = Parser(tokens).parse()
        interpreter = Interpreter(ast)
        interpreter.interpret()
        value = interpreter.evaluate(VariableExpression(identifier("a")))
        self.assertEqual(4, value)

    def assertError(self, message, program):
        threw = False

        try:
            program()
        except TypeError as error:
            threw = True
            self.assertEqual(message, error.message)

        self.assertTrue(threw, "Expected code to error")


def run_expr(code):
    (tokens, _) = Scanner(f"{code};").scan()
    (ast, _) = Parser(tokens).parse()
    return Interpreter(Program([])).evaluate(ast.statements[0].expression)
