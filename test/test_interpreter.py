from test import TestCase
from lib.error import TypeError, RuntimeError
from lib.parser import Parser
from lib.scanner import Scanner
from lib.resolver import Resolver
from lib.interpreter import Interpreter
from lib.error import UninitializedVariableError
from lib.io import FakePrinter
from lib.token import identifier
from lib.function import Function
from lib import ast


class InterpreterTest(TestCase):
    def setUp(self):
        Interpreter.printer = FakePrinter

    def test_global_environment(self):
        interpreter = Interpreter.from_code("var x = clock();")

        self.assertTrue(isinstance(interpreter.evaluate(Parser.parse_expr("x")), float))

    def test_multiple_interpretations(self):
        interpreter = Interpreter()

        a_ast = Parser.parse_code("var succ = \\x -> x + 1;")
        a_bindings = Resolver(a_ast).run()

        interpreter.interpret(a_ast, a_bindings)

        b_ast = Parser.parse_code("print succ(4);")
        b_bindings = Resolver(a_ast).run()

        interpreter.interpret(b_ast, b_bindings)

        self.assertEqual(["5"], interpreter.printer.get())

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

    def test_if_statements(self):
        interpreter = Interpreter.from_code("if (true) { print 1; } else { print 2; }")
        self.assertEqual(["1"], interpreter.printer.get())

        interpreter = Interpreter.from_code("if (3 < 1) { print 1; } else { print 2; }")
        self.assertEqual(["2"], interpreter.printer.get())

        interpreter = Interpreter.from_code("if (false) { print 1; }")
        self.assertEqual([], interpreter.printer.get())

    def test_logical_operators(self):
        interpreter = Interpreter()

        self.assertEqual(True, interpreter.evaluate(Parser.parse_expr("true and true")))
        self.assertEqual(
            False, interpreter.evaluate(Parser.parse_expr("true and false"))
        )
        self.assertEqual(True, interpreter.evaluate(Parser.parse_expr("true or false")))
        self.assertEqual(
            False, interpreter.evaluate(Parser.parse_expr("false or false"))
        )

    def test_while_statements(self):
        interpreter = Interpreter.from_code(
            "var a = 1; while (a < 3) { print(a); a = a + 1; }"
        )

        self.assertEqual(["1", "2"], interpreter.printer.get())

    def test_for_loops(self):
        interpreter = Interpreter.from_code(
            "for (var a = 0; a < 3; a = a + 1) { print a; }"
        )
        self.assertEqual(["0", "1", "2"], interpreter.printer.get())

    def test_function_declaration(self):
        interpreter = Interpreter.from_code("fun foo(a) { }")

        foo = interpreter.globals.get(identifier("foo"))

        self.assertTrue(isinstance(foo, Function))
        self.assertEqual("foo", foo.name())
        self.assertEqual([identifier("a")], foo.parameters())
        self.assertEqual(ast.Block([]), foo.body())

    def test_function_call(self):
        interpreter = Interpreter.from_code(
            """
fun foo(a) {
    print a;
}

foo(40 + 2);
"""
        )

        self.assertEqual(["42"], interpreter.printer.get())

    def test_calling_non_callable(self):
        try:
            interpreter = Interpreter.from_code("var a = 1; a();")
        except RuntimeError as e:
            self.assertEqual("Can only call functions or classes", e.message)
        else:
            self.fail("Expected exception")

    def test_calling_function_with_wrong_number_of_arguments(self):
        try:
            Interpreter.from_code("fun foo(a) {} foo();")
        except RuntimeError as e:
            self.assertEqual("Expected 1 arguments but got 0", e.message)
        else:
            self.fail("Expected exception")

        try:
            Interpreter.from_code("fun foo(a) {} foo(1, 2);")
        except RuntimeError as e:
            self.assertEqual("Expected 1 arguments but got 2", e.message)
        else:
            self.fail("Expected exception")

    def test_return_statement(self):
        interpreter = Interpreter.from_code(
            """
fun foo(x) {
    return 40 + x;
}

print foo(2);
"""
        )

        self.assertEqual(["42"], interpreter.printer.get())

    def test_nested_functions(self):
        interpreter = Interpreter.from_code(
            """
fun foo() {
    fun bar(y) {
        return 40 + y;
    }

    return bar;
}
"""
        )

        self.assertEqual(43, interpreter.evaluate(Parser.parse_expr("foo()(3)")))

    def test_recursion(self):
        interpreter = Interpreter.from_code(
            """
fun foo(n) {
    if (n == 0) {
        return n;
    }

    return n + foo(n - 1);
}
"""
        )

        self.assertEqual(6, interpreter.evaluate(Parser.parse_expr("foo(3)")))

    def test_closure(self):
        interpreter = Interpreter.from_code(
            """
fun factory() {
    var i = 0;

    fun step() {
        i = i + 1;
        return i;
    }

    return step;
}

var step = factory();
"""
        )

        self.assertEqual(1, interpreter.evaluate(Parser.parse_expr("step()")))
        self.assertEqual(2, interpreter.evaluate(Parser.parse_expr("step()")))
        self.assertEqual(3, interpreter.evaluate(Parser.parse_expr("step()")))

    def test_anonymous_functions(self):
        interpreter = Interpreter.from_code(
            """
fun twice(f) {
    return fun (x) { return f(f(x)); };
}

var two_sucks = twice(fun (x) { return x + 1; });
"""
        )

        self.assertEqual(3, interpreter.evaluate(Parser.parse_expr("two_sucks(1)")))

    def test_lambda_expressions(self):
        interpreter = Interpreter.from_code(
            """
var twice = \\f -> \\x -> f(f(x));
var two_sucks = twice(\\x -> x + 1);
"""
        )

        self.assertEqual(3, interpreter.evaluate(Parser.parse_expr("two_sucks(1)")))

    def test_classes(self):
        interpreter = Interpreter.from_code(
            """
class Foo {
    init(baz) {
        this.baz = baz;
    }

    bar() {
        return "hey " + this.baz;
    }
}

print Foo("qux").bar();
"""
        )
        self.assertEqual(["hey qux"], interpreter.printer.get())

    def test_initializer_returns_instance_implicitly(self):
        interpreter = Interpreter.from_code(
            """
class Foo {
    init() {}
}

print Foo().init();
"""
        )
        self.assertEqual(["<instance Foo>"], interpreter.printer.get())

    def test_superclass_must_be_class(self):
        try:
            interpreter = Interpreter.from_code("var Bar = 1; class Foo < Bar {}")
        except RuntimeError as e:
            self.assertEqual("Superclass must be a class", e.message)
        else:
            self.fail("Expected exception")

    def test_inheritance(self):
        interpreter = Interpreter.from_code(
            """
class Bar {
    bar() {
        return 42;
    }
}

class Foo < Bar {}

print Foo().bar();
"""
        )
        self.assertEqual(["42"], interpreter.printer.get())

    def test_super(self):
        interpreter = Interpreter.from_code(
            """
class Bar {
    boo() {
        return 21;
    }
}

class Foo < Bar {
    boo() {
        return super.boo() * 2;
    }
}


print Foo().boo();
"""
        )

        self.assertEqual(["42"], interpreter.printer.get())

    def test_missing_method_on_super(self):
        try:
            interpreter = Interpreter.from_code(
                """
    class Bar {}
    class Foo < Bar {
        boo() {
            return super.boo() * 2;
        }
    }

    print Foo().boo();
    """
            )
        except RuntimeError as e:
            self.assertEqual("Undefined method 'boo'", e.message)
        else:
            self.fail("Expected exception")


def evaluate_expr(code):
    interpreter = Interpreter()
    expression = Parser.parse_expr(code)
    return interpreter.evaluate(expression)
