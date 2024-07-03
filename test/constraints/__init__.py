import pathlib
import unittest

from colc import compile_file, TextFile
from test.utils import FileTestMeta


class ConstraintTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        obj = compile_file(TextFile(pathlib.Path('test.col'), input))
        self.assertEqual(output, repr(obj.constraint))
