import unittest

from ..utils import FileTestMeta

from frontend import parse
from backend import encode_constraint


class ConstraintTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        constraint = parse(input).main_constraint()
        encoded = encode_constraint(constraint)

        self.assertEqual(output, repr(encoded))
