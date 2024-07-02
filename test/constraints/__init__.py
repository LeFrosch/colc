import unittest

from utils import FileTestMeta

from colc.frontend import parse
from colc.backend.file import File
from colc.backend.constraint import process_constraint


class ConstraintTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        file = File(parse(input))
        encoded = process_constraint(file)

        self.assertEqual(output, repr(encoded))
