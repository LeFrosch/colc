import pathlib
import unittest
import colc

from test.utils import FileTestMeta


class ConstraintTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        obj = colc.compile_file(colc.TextFile(pathlib.Path('test.col'), input))
        self.assertEqual(output, repr(obj.constraint))
