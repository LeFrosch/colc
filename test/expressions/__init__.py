import unittest
from typing import cast

from colc.frontend import ast
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

    def do_test(self, input: str):
        for line in input.splitlines():
            with self.subTest(line):
                expr, expected = line.split(' -> ')
                self.do_single_test(expr, expected)
