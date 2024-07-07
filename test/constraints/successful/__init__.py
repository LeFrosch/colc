import unittest

from test.utils import FileTestMeta, compile_constraint


class FileTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        _, constraint = compile_constraint(input)
        self.assertEqual(output, repr(constraint))
