from unittest import skip
from test import TestCase
from lib.parser import Parser
from lib.io import FakePrinter
from lib.resolver import Resolver
from lib.interpreter import Interpreter
from lib.error import CompileErrors


class ResolverTest(TestCase):
    def setUp(self):
        Interpreter.printer = FakePrinter

    def test_canonical_example(self):
        ast = Parser.parse_code(
            """
var a = "global";
{
  fun showA() {
    print a;
  }

  showA();
  var a = "block";
  showA();
}
"""
        )

        bindings = Resolver(ast).run()

        interpreter = Interpreter(bindings)
        interpreter.interpret(ast)

        self.assertEqual(["global", "global"], interpreter.printer.get())

    def test_nested_example(self):
        ast = Parser.parse_code(
            """
fun f() {
    var b;

    var g = \\a -> a + b;

    fun id(x) { return x; }

    b;
}
"""
        )

        bindings = Resolver(ast).run()
        bindings = [(node.variable.lexeme, depth) for node, depth in bindings.items()]

        self.assertEqual([("a", 0), ("b", 1), ("x", 0), ("b", 0)], bindings)

    def test_double_declarations_error(self):
        ast = Parser.parse_code(
            """
fun f() {
    var a = "global";
    var a = "again";
}
"""
        )

        try:
            Resolver(ast).run()
        except CompileErrors as e:
            self.assertEqual(["Variable [a] is already defined"], e.messages())
        else:
            self.fail("Expected exception")

    def test_mid_initialization_access_error(self):
        ast = Parser.parse_code(
            """
fun f() {
    var a = a;
}
"""
        )

        try:
            Resolver(ast).run()
        except CompileErrors as e:
            self.assertEqual(
                ["Variable [a] accessed inside its own initializer"], e.messages()
            )
        else:
            self.fail("Expected exception")

    @skip("resolver does not work for globals")
    def test_errors_for_global_variables(self):
        ast = Parser.parse_code(
            """
var a = a;

var d = 1;
var d = 2;
"""
        )

        try:
            Resolver(ast).run()
        except CompileErrors as e:
            self.assertEqual(
                [
                    "Variable [a] accessed inside its own initializer",
                    "Variable [d] is already defined",
                ],
                e.messages(),
            )
        else:
            self.fail("Expected exception")
