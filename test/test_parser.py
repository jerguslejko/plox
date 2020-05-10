from test import TestCase
import lib.ast as ast
from lib.parser import Parser
from lib.scanner import Scanner
from lib.token import Token, Type
from lib.error import ParseError, ParseErrors


class ParserTest(TestCase):
    def test_it_parses_literals(self):
        self.assertEqual(
            ast.LiteralExpression(1), Parser.parse_expr("1"),
        )

        self.assertEqual(
            ast.LiteralExpression(1.2), Parser.parse_expr("1.2"),
        )

        self.assertEqual(
            ast.LiteralExpression("hello"), Parser.parse_expr('"hello"'),
        )
        self.assertEqual(
            ast.LiteralExpression("hello"), Parser.parse_expr("'hello'"),
        )

        self.assertEqual(
            ast.LiteralExpression(True), Parser.parse_expr("true"),
        )

        self.assertEqual(
            ast.LiteralExpression(False), Parser.parse_expr("false"),
        )

        self.assertEqual(
            ast.LiteralExpression(None), Parser.parse_expr("nil"),
        )

        self.assertEqual(
            ast.GroupingExpression(ast.LiteralExpression(1)), Parser.parse_expr("(1)")
        )

    def test_it_parses_equality(self):
        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.EQUAL_EQUAL, "==", None, 1),
                ast.LiteralExpression(1),
            ),
            Parser.parse_expr("1 == 1"),
        )

    def test_it_parses_comparison(self):
        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.LESS, "<", None, 1),
                ast.LiteralExpression(1),
            ),
            Parser.parse_expr("1 < 1"),
        )

        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.LESS_EQUAL, "<=", None, 1),
                ast.LiteralExpression(1),
            ),
            Parser.parse_expr("1 <= 1"),
        )

        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.GREATER, ">", None, 1),
                ast.LiteralExpression(1),
            ),
            Parser.parse_expr("1 > 1"),
        )

        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.GREATER_EQUAL, ">=", None, 1),
                ast.LiteralExpression(1),
            ),
            Parser.parse_expr("1 >= 1"),
        )

    def test_it_parses_addition(self):
        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.PLUS, "+", None, 1),
                ast.LiteralExpression(1),
            ),
            Parser.parse_expr("1 + 1"),
        )

        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.MINUS, "-", None, 1),
                ast.LiteralExpression(1),
            ),
            Parser.parse_expr("1 - 1"),
        )

    def test_it_parses_multiplicate(self):
        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.STAR, "*", None, 1),
                ast.LiteralExpression(1),
            ),
            Parser.parse_expr("1 * 1"),
        )

        self.assertEqual(
            ast.BinaryExpression(
                ast.LiteralExpression(1),
                Token(Type.SLASH, "/", None, 1),
                ast.LiteralExpression(1),
            ),
            Parser.parse_expr("1 / 1"),
        )

    def test_it_parses_unary(self):
        self.assertEqual(
            ast.UnaryExpression(
                Token(Type.BANG, "!", None, 1), ast.LiteralExpression(True),
            ),
            Parser.parse_expr("!true"),
        )

        self.assertEqual(
            ast.UnaryExpression(
                Token(Type.MINUS, "-", None, 1), ast.LiteralExpression(42),
            ),
            Parser.parse_expr("-42"),
        )

    def test_it_respects_operator_precedence(self):
        self.assertEqual(
            ast.BinaryExpression(
                ast.BinaryExpression(
                    ast.LiteralExpression(1),
                    Token(Type.PLUS, "+", None, 1),
                    ast.BinaryExpression(
                        ast.BinaryExpression(
                            ast.LiteralExpression(2),
                            Token(Type.STAR, "*", None, 1),
                            ast.LiteralExpression(3),
                        ),
                        Token(Type.SLASH, "/", None, 1),
                        ast.UnaryExpression(
                            Token(Type.MINUS, "-", None, 1), ast.LiteralExpression(4),
                        ),
                    ),
                ),
                Token(Type.PLUS, "+", None, 1),
                ast.GroupingExpression(
                    ast.BinaryExpression(
                        ast.LiteralExpression(5),
                        Token(Type.STAR, "*", None, 1),
                        ast.UnaryExpression(
                            Token(Type.BANG, "!", None, 1), ast.LiteralExpression(True)
                        ),
                    )
                ),
            ),
            Parser.parse_expr("1 + 2 * 3 / -4 + (5 * !true)"),
        )

    def test_it_parses_ternary(self):
        self.assertEqual(
            ast.TernaryExpression(
                ast.LiteralExpression(1),
                Token(Type.QUESTION_MARK, "?", None, 1),
                ast.LiteralExpression(2),
                ast.LiteralExpression(3),
            ),
            Parser.parse_expr("1 ? 2 : 3"),
        )

        self.assertEqual(
            ast.TernaryExpression(
                ast.LiteralExpression(1),
                Token(Type.QUESTION_MARK, "?", None, 1),
                ast.LiteralExpression(2),
                ast.TernaryExpression(
                    ast.LiteralExpression(3),
                    Token(Type.QUESTION_MARK, "?", None, 1),
                    ast.LiteralExpression(4),
                    ast.LiteralExpression(5),
                ),
            ),
            Parser.parse_expr("1 ? 2 : 3 ? 4 : 5"),
        )

    def test_synchronization(self):
        tokens = Scanner("( 1; 1;").scan()

        try:
            tree = Parser(tokens).parse()
        except ParseErrors as e:
            self.assertEqual(["Expected ')' after expression"], e.messages())
        else:
            self.fail("Expected exception")

    def test_it_parses_statements(self):
        self.assertParseTree(
            ast.Program(
                [
                    ast.ExpressionStatement(ast.LiteralExpression(1)),
                    ast.ExpressionStatement(ast.LiteralExpression(2)),
                ]
            ),
            "1;\n2;",
        )

    def test_it_parses_print_statement(self):
        self.assertParseTree(
            ast.Program([ast.PrintStatement([ast.LiteralExpression(1)])]), "print 1;",
        )

        self.assertParseTree(
            ast.Program(
                [
                    ast.PrintStatement(
                        [ast.LiteralExpression(1), ast.LiteralExpression(2)]
                    )
                ]
            ),
            "print 1, 2;",
        )

    def test_it_parses_variable_declaration(self):
        self.assertParseTree(
            ast.Program(
                [ast.VariableDeclaration(Token(Type.IDENTIFIER, "a", "a", 1), None)]
            ),
            "var a;",
        )

    def test_it_parses_variable_declaration_with_initializer(self):
        self.assertParseTree(
            ast.Program(
                [
                    ast.VariableDeclaration(
                        Token(Type.IDENTIFIER, "a", "a", 1), ast.LiteralExpression(4)
                    )
                ]
            ),
            "var a = 4;",
        )

    def test_it_parser_variable_expression(self):
        self.assertParseTree(
            ast.Program(
                [
                    ast.ExpressionStatement(
                        ast.VariableExpression(Token(Type.IDENTIFIER, "a", "a", 1))
                    )
                ]
            ),
            "a;",
        )

    def test_it_parses_variable_assignment(self):
        self.assertParseTree(
            ast.Program(
                [
                    ast.ExpressionStatement(
                        ast.AssignmentExpression(
                            Token(Type.IDENTIFIER, "a", "a", 1),
                            Token(Type.EQUAL, "=", None, 1),
                            ast.LiteralExpression(3),
                        )
                    )
                ]
            ),
            "a = 3;",
        )

    def test_it_parses_block(self):
        self.assertParseTree(
            ast.Program(
                [ast.Block([ast.ExpressionStatement(ast.LiteralExpression(None))])]
            ),
            "{ nil; }",
        )

    def test_it_fails_when_assignment_target_is_not_variable(self):
        try:
            Parser.parse_code("var a; var b; a + b = 1")
        except ParseErrors as e:
            pass
        else:
            self.fail("Expected exception")

    def test_if_statements(self):
        self.assertParseTree(
            ast.Program(
                [
                    ast.IfStatement(
                        ast.LiteralExpression(True),
                        ast.ExpressionStatement(ast.LiteralExpression(1)),
                        None,
                    )
                ]
            ),
            "if (true) 1;",
        )

        self.assertParseTree(
            ast.Program(
                [
                    ast.IfStatement(
                        ast.LiteralExpression(True),
                        ast.ExpressionStatement(ast.LiteralExpression(1)),
                        ast.ExpressionStatement(ast.LiteralExpression(2)),
                    )
                ]
            ),
            "if (true) 1; else 2;",
        )

        self.assertParseTree(
            ast.Program(
                [
                    ast.IfStatement(
                        ast.LiteralExpression(True),
                        ast.IfStatement(
                            ast.LiteralExpression(False),
                            ast.ExpressionStatement(ast.LiteralExpression(3)),
                            ast.ExpressionStatement(ast.LiteralExpression(2)),
                        ),
                        None,
                    )
                ]
            ),
            "if (true) if (false) 3; else 2;",
        )

    def test_logical_operators(self):
        self.assertParseTree(
            ast.Program(
                [
                    ast.ExpressionStatement(
                        ast.LogicalExpression(
                            ast.LogicalExpression(
                                ast.LiteralExpression(1),
                                Token(Type.AND, "and", None, 1),
                                ast.LiteralExpression(2),
                            ),
                            Token(Type.OR, "or", None, 1),
                            ast.LiteralExpression(3),
                        )
                    )
                ]
            ),
            "1 and 2 or 3;",
        )

    def test_while_expression(self):
        self.assertParseTree(
            ast.Program(
                [
                    ast.WhileStatement(
                        Token(Type.WHILE, "while", None, 1),
                        ast.LiteralExpression(True),
                        ast.Block([]),
                    )
                ]
            ),
            "while (true) {}",
        )

    def test_for_expression(self):
        self.assertParseTree(
            ast.Program(
                [
                    ast.Block(
                        [
                            ast.WhileStatement(
                                Token(Type.FOR, "for", None, 1),
                                ast.LiteralExpression(True),
                                ast.Block([]),
                            )
                        ]
                    )
                ]
            ),
            "for (;;) {}",
        )

        self.assertParseTree(
            ast.Program(
                [
                    ast.Block(
                        [
                            ast.VariableDeclaration(
                                Token(Type.IDENTIFIER, "a", "a", 1),
                                ast.LiteralExpression(0),
                            ),
                            ast.WhileStatement(
                                Token(Type.FOR, "for", None, 1),
                                ast.LiteralExpression(True),
                                ast.Block([]),
                            ),
                        ]
                    )
                ]
            ),
            "for (var a = 0;;) {}",
        )

        self.assertParseTree(
            ast.Program(
                [
                    ast.Block(
                        [
                            ast.VariableDeclaration(
                                Token(Type.IDENTIFIER, "a", "a", 1),
                                ast.LiteralExpression(0),
                            ),
                            ast.WhileStatement(
                                Token(Type.FOR, "for", None, 1),
                                ast.BinaryExpression(
                                    ast.VariableExpression(
                                        Token(Type.IDENTIFIER, "a", "a", 1)
                                    ),
                                    Token(Type.LESS, "<", None, 1),
                                    ast.LiteralExpression(10),
                                ),
                                ast.Block([]),
                            ),
                        ]
                    )
                ]
            ),
            "for (var a = 0; a < 10;) {}",
        )

        self.assertParseTree(
            ast.Program(
                [
                    ast.Block(
                        [
                            ast.VariableDeclaration(
                                Token(Type.IDENTIFIER, "a", "a", 1),
                                ast.LiteralExpression(0),
                            ),
                            ast.WhileStatement(
                                Token(Type.FOR, "for", None, 1),
                                ast.BinaryExpression(
                                    ast.VariableExpression(
                                        Token(Type.IDENTIFIER, "a", "a", 1)
                                    ),
                                    Token(Type.LESS, "<", None, 1),
                                    ast.LiteralExpression(10),
                                ),
                                ast.Block(
                                    [
                                        ast.ExpressionStatement(
                                            ast.AssignmentExpression(
                                                Token(Type.IDENTIFIER, "a", "a", 1),
                                                Token(Type.EQUAL, "=", None, 1),
                                                ast.BinaryExpression(
                                                    ast.VariableExpression(
                                                        Token(
                                                            Type.IDENTIFIER, "a", "a", 1
                                                        )
                                                    ),
                                                    Token(Type.PLUS, "+", None, 1),
                                                    ast.LiteralExpression(1),
                                                ),
                                            )
                                        ),
                                    ]
                                ),
                            ),
                        ]
                    )
                ]
            ),
            "for (var a = 0; a < 10; a = a + 1) {}",
        )

        self.assertParseTree(
            ast.Program(
                [
                    ast.Block(
                        [
                            ast.ExpressionStatement(
                                ast.AssignmentExpression(
                                    Token(Type.IDENTIFIER, "a", "a", 1),
                                    Token(Type.EQUAL, "=", None, 1),
                                    ast.LiteralExpression(0),
                                )
                            ),
                            ast.WhileStatement(
                                Token(Type.FOR, "for", None, 1),
                                ast.LiteralExpression(True),
                                ast.Block([]),
                            ),
                        ]
                    )
                ]
            ),
            "for (a = 0;;) {}",
        )

        self.assertParseTree(
            ast.Program(
                [
                    ast.Block(
                        [
                            ast.WhileStatement(
                                Token(Type.FOR, "for", None, 1),
                                ast.LiteralExpression(True),
                                ast.Block(
                                    [
                                        ast.Block(
                                            [
                                                ast.ExpressionStatement(
                                                    ast.LiteralExpression(2)
                                                )
                                            ]
                                        ),
                                        ast.ExpressionStatement(
                                            ast.LiteralExpression(1)
                                        ),
                                    ]
                                ),
                            ),
                        ]
                    )
                ]
            ),
            "for (;;1) { 2; }",
        )

    def test_function_calls(self):
        self.assertParseTree(
            ast.Program(
                [
                    ast.ExpressionStatement(
                        ast.CallExpression(
                            ast.VariableExpression(
                                Token(Type.IDENTIFIER, "foo", "foo", 1)
                            ),
                            Token(Type.RIGHT_PAREN, ")", None, 1),
                            [],
                        )
                    )
                ]
            ),
            "foo();",
        )

        self.assertParseTree(
            ast.Program(
                [
                    ast.ExpressionStatement(
                        ast.CallExpression(
                            ast.VariableExpression(
                                Token(Type.IDENTIFIER, "foo", "foo", 1)
                            ),
                            Token(Type.RIGHT_PAREN, ")", None, 1),
                            [ast.LiteralExpression(1)],
                        )
                    )
                ]
            ),
            "foo(1);",
        )

        self.assertParseTree(
            ast.Program(
                [
                    ast.ExpressionStatement(
                        ast.CallExpression(
                            ast.VariableExpression(
                                Token(Type.IDENTIFIER, "foo", "foo", 1)
                            ),
                            Token(Type.RIGHT_PAREN, ")", None, 1),
                            [
                                ast.LiteralExpression(1),
                                ast.VariableExpression(
                                    Token(Type.IDENTIFIER, "b", "b", 1)
                                ),
                            ],
                        )
                    )
                ]
            ),
            "foo(1, b);",
        )

        self.assertParseTree(
            ast.Program(
                [
                    ast.ExpressionStatement(
                        ast.CallExpression(
                            ast.CallExpression(
                                ast.VariableExpression(
                                    Token(Type.IDENTIFIER, "f", "f", 1)
                                ),
                                Token(Type.RIGHT_PAREN, ")", None, 1),
                                [ast.LiteralExpression(1)],
                            ),
                            Token(Type.RIGHT_PAREN, ")", None, 1),
                            [ast.LiteralExpression(2)],
                        )
                    )
                ]
            ),
            "f(1)(2);",
        )

    def test_maximum_argument_count(self):
        try:
            Parser.parse_code("f(%s);" % ", ".join(["1"] * 256))
        except ParseErrors as e:
            self.assertEqual(["Maximum argument count of 255 exceeded"], e.messages())
        else:
            self.fail("Expected exception")

    def test_function_declaration(self):
        self.assertParseTree(
            ast.Program(
                [
                    ast.FunctionDeclaration(
                        Token(Type.IDENTIFIER, "foo", "foo", 1), [], ast.Block([])
                    )
                ]
            ),
            "fun foo() {}",
        )

        self.assertParseTree(
            ast.Program(
                [
                    ast.FunctionDeclaration(
                        Token(Type.IDENTIFIER, "foo", "foo", 1),
                        [Token(Type.IDENTIFIER, "a", "a", 1)],
                        ast.Block([]),
                    )
                ]
            ),
            "fun foo(a) {}",
        )

        self.assertParseTree(
            ast.Program(
                [
                    ast.FunctionDeclaration(
                        Token(Type.IDENTIFIER, "foo", "foo", 1),
                        [
                            Token(Type.IDENTIFIER, "a", "a", 1),
                            Token(Type.IDENTIFIER, "b", "b", 1),
                        ],
                        ast.Block([]),
                    )
                ]
            ),
            "fun foo(a, b) {}",
        )

    def test_maximum_parameter_count(self):
        try:
            Parser.parse_code("fun f(%s) {}" % ", ".join(["x"] * 256))
        except ParseErrors as e:
            self.assertEqual(["Maximum parameter count of 255 exceeded"], e.messages())
        else:
            self.fail("Expected exception")

    def test_return_statement(self):
        self.assertParseTree(
            ast.Program(
                [
                    ast.ReturnStatement(
                        ast.LiteralExpression(42), Token(Type.RETURN, "return", None, 1)
                    )
                ]
            ),
            "return 42;",
        )

        self.assertParseTree(
            ast.Program(
                [
                    ast.ReturnStatement(
                        ast.LiteralExpression(None),
                        Token(Type.RETURN, "return", None, 1),
                    )
                ]
            ),
            "return;",
        )

    def test_anonymous_function_expression(self):
        self.assertParseTree(
            ast.Program(
                [
                    ast.VariableDeclaration(
                        Token(Type.IDENTIFIER, "f", "f", 1),
                        ast.FunctionExpression(
                            [Token(Type.IDENTIFIER, "x", "x", 1)],
                            ast.Block(
                                [
                                    ast.ReturnStatement(
                                        ast.VariableExpression(
                                            Token(Type.IDENTIFIER, "x", "x", 1)
                                        ),
                                        Token(Type.RETURN, "return", None, 1),
                                    )
                                ]
                            ),
                        ),
                    )
                ]
            ),
            "var f = fun (x) { return x; };",
        )

    def test_lambda_expressions(self):
        self.assertParseTree(
            ast.Program(
                [
                    ast.VariableDeclaration(
                        Token(Type.IDENTIFIER, "f", "f", 1),
                        ast.LambdaExpression(
                            [],
                            Token(Type.ARROW, "->", None, 1),
                            ast.VariableExpression(Token(Type.IDENTIFIER, "x", "x", 1)),
                        ),
                    )
                ]
            ),
            "var f = \\ -> x;",
        )

        self.assertParseTree(
            ast.Program(
                [
                    ast.VariableDeclaration(
                        Token(Type.IDENTIFIER, "f", "f", 1),
                        ast.LambdaExpression(
                            [Token(Type.IDENTIFIER, "x", "x", 1)],
                            Token(Type.ARROW, "->", None, 1),
                            ast.VariableExpression(Token(Type.IDENTIFIER, "x", "x", 1)),
                        ),
                    )
                ]
            ),
            "var f = \\x -> x;",
        )

        self.assertParseTree(
            ast.Program(
                [
                    ast.VariableDeclaration(
                        Token(Type.IDENTIFIER, "f", "f", 1),
                        ast.LambdaExpression(
                            [
                                Token(Type.IDENTIFIER, "x", "x", 1),
                                Token(Type.IDENTIFIER, "y", "y", 1),
                            ],
                            Token(Type.ARROW, "->", None, 1),
                            ast.VariableExpression(Token(Type.IDENTIFIER, "x", "x", 1)),
                        ),
                    )
                ]
            ),
            "var f = \\x, y -> x;",
        )

    def test_wild_function_expression(self):
        self.assertParseTree(
            ast.Program(
                [ast.ExpressionStatement(ast.FunctionExpression([], ast.Block([])))]
            ),
            "fun () {}",
        )

    def test_is_expr(self):
        self.assertTrue(Parser.is_expr("1"))
        self.assertFalse(Parser.is_expr("1;"))

    # helpers

    def assertParseTree(self, tree, code):
        self.assertAstMatches(tree, Parser.parse_code(code))
