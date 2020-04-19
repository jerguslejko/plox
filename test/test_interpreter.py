import unittest
from lib.error import TypeError
from lib.parser import Parser
from lib.scanner import Scanner
from lib.interpreter import Interpreter
from lib.error import UninitializedVariableError
from lib.io import FakePrinter


class InterpreterTest(unittest.TestCase):
    def setUp(self):
        Interpreter.printer = FakePrinter

    def test_it_interprets_literals(self):
        self.assertEqual(1, evaluate_expr("1"))
        self.assertEqual(2.4, evaluate_expr("2.4"))
        self.assertEqual("hi", evaluate_expr('"hi"'))
        self.assertEqual(True, evaluate_expr("true"))
        self.assertEqual(False, evaluate_expr("false"))
        self.assertEqual(None, evaluate_expr("nil"))

    def test_it_interprets_grouping_expression(self):
        self.assertEqual(None, evaluate_expr("(nil)"))

    def test_it_interprets_unary_expressions(self):
        self.assertEqual(-2, evaluate_expr("-2"))
        self.assertEqual(2, evaluate_expr("--2"))
        self.assertEqual(True, evaluate_expr("!false"))
        self.assertEqual(False, evaluate_expr("!!false"))

    def test_it_interprets_binary_expressions(self):
        self.assertEqual(2, evaluate_expr("1 + 1"))
        self.assertEqual(-2, evaluate_expr("1 - 3"))
        self.assertEqual(8, evaluate_expr("1 * 8"))
        self.assertEqual(2, evaluate_expr("4 / 2"))
        self.assertEqual("foobar", evaluate_expr('"foo" + "bar"'))
        self.assertEqual("foo", evaluate_expr('"foobar" - "bar"'))
        self.assertEqual(False, evaluate_expr("1 > 2"))
        self.assertEqual(True, evaluate_expr("2 > 1"))
        self.assertEqual(True, evaluate_expr("1 < 2"))
        self.assertEqual(False, evaluate_expr("2 < 1"))
        self.assertEqual(True, evaluate_expr("1 <= 2"))
        self.assertEqual(True, evaluate_expr("2 <= 2"))
        self.assertEqual(False, evaluate_expr("3 <= 2"))
        self.assertEqual(False, evaluate_expr("1 >= 2"))
        self.assertEqual(True, evaluate_expr("2 >= 2"))
        self.assertEqual(True, evaluate_expr("3 >= 2"))
        self.assertEqual(True, evaluate_expr("1 == 1"))
        self.assertEqual(False, evaluate_expr("1 == 2"))
        self.assertEqual(False, evaluate_expr('1 == "1"'))
        self.assertEqual(True, evaluate_expr('"foo" == "foo"'))
        self.assertEqual(False, evaluate_expr('"foo" == "bar"'))
        self.assertEqual(True, evaluate_expr("nil == nil"))
        self.assertEqual(False, evaluate_expr("nil == 2"))
        self.assertEqual(False, evaluate_expr("1 != 1"))
        self.assertEqual(True, evaluate_expr("1 != 2"))
        self.assertEqual(True, evaluate_expr("true == true"))
        self.assertEqual(False, evaluate_expr("true == false"))

    def test_it_interprets_ternary_expressions(self):
        self.assertEqual(1, evaluate_expr("true ? 1 : 2"))
        self.assertEqual(2, evaluate_expr("false ? 1 : 2"))
        self.assertEqual(1, evaluate_expr("!false ? 1 : 2"))

    def test_it_validates_types(self):
        def assertError(message, program):
            threw = False

            try:
                program()
            except TypeError as error:
                threw = True
                self.assertEqual(message, error.message)

            self.assertTrue(threw, "Expected code to error")

        assertError(
            "Operand of (-) must be of type number, nil given",
            lambda: evaluate_expr("-nil"),
        )
        assertError(
            "Operand of (!) must be of type bool, number given",
            lambda: evaluate_expr("!2.3"),
        )
        assertError(
            "Operands of (+) must be of the same type. number and string given",
            lambda: evaluate_expr("1 + 'foo'"),
        )
        assertError(
            "Operands of (+) must be of type number or string, bool given",
            lambda: evaluate_expr("true + false"),
        )

    def test_it_interprets_variable_declarations_and_expressions(self):
        interpreter = Interpreter.from_code("var a = 4;")
        value = interpreter.evaluate(Parser.parse_expr("a"))
        self.assertEqual(4, value)

    def test_it_interprets_variable_assignments(self):
        interpreter = Interpreter.from_code("var a;")
        value = interpreter.evaluate(Parser.parse_expr("a = 3"))
        self.assertEqual(3, value)

        value = interpreter.evaluate(Parser.parse_expr("a"))
        self.assertEqual(3, value)

    def test_blocks_create_scopes(self):
        interpreter = Interpreter.from_code(
            "var a = 1; var b = 2; { var a = 3; b = 4; }"
        )

        self.assertEqual(1, interpreter.evaluate(Parser.parse_expr("a")))
        self.assertEqual(4, interpreter.evaluate(Parser.parse_expr("b")))

    def test_accessing_uninitialized_variables_throws(self):
        interpreter = Interpreter.from_code("var a;")

        try:
            interpreter.evaluate(Parser.parse_expr("a"))
        except UninitializedVariableError:
            pass
        else:
            self.fail("Expected exception")


def evaluate_expr(code):
    interpreter = Interpreter.from_code(f"{code};")
    return interpreter.evaluate(interpreter.ast.statements[0].expression)
