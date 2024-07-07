import unittest

from test.utils import FileTestMeta, compile_constraint


class FileTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        self.assertEqual(output, repr(compile_constraint(input)))
