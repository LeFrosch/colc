import unittest

from utils import FileTestMeta

from colc.frontend import parse
from colc.backend import process


class ConstraintTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        obj = process(parse(input))
        self.assertEqual(output, repr(obj.constraint))
