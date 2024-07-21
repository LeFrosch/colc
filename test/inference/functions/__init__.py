import unittest
from typing import cast

from colc.common import first
from colc.frontend import ast
from colc.backend._process_mapping import VisitorImpl

from test.utils import FileTestMeta, create_test_context


def _compile_function(input: str) -> ast.FDefinition:
    ctx = create_test_context(input)
    return cast(ast.FDefinition, ctx.file.definitions[0])


class FileTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, type: str):
        func = _compile_function(input)
        args = ', '.join(['root.attr'] * len(func.parameters))

        file = '%s map main { var r = %s(%s); }' % (input, func.identifier.name, args)
        ctx = create_test_context(file)

        mapping = first(ctx.file.mappings)
        call = mapping.block.statements[0].expression
        returns = VisitorImpl(ctx).accept_expr(call)

        self.assertEqual(type, repr(returns))
