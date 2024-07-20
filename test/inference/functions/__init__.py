import unittest
from typing import cast

from colc.frontend import ast
from colc.common import AnyValue
from colc.backend._process_mapping import VisitorImpl
from test.utils import FileTestMeta, create_test_context


class FileTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_single_test(self, expr, expected):
        text = 'map main { r = %s; }' % expr
        ctx = create_test_context(text)

        func = ctx.file.mappings[0]
        stmt = cast(ast.FStatementAssign, func.block.statements[0])
        expr = stmt.expression

        value = VisitorImpl(ctx).accept_expr(expr)
        self.assertEqual(repr(value), expected)

    def do_test(self, input: str, type: str):
        ctx = create_test_context(input)

        func = ctx.file.definitions[0]
        visitor = VisitorImpl(ctx)

        for i, param in enumerate(func.parameters):
            visitor.scope.insert_runtime(param, AnyValue, i, True)

        visitor.accept(func.block)
        _, returns = visitor.scope.returns()

        self.assertEqual(repr(returns), type)
