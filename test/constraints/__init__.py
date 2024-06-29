import unittest

from utils import FileTestMeta

from frontend import parse
from backend.file import File
from backend.constraint import encode_main_constraint


class ConstraintTest(unittest.TestCase, metaclass=FileTestMeta, path=__file__):
    def do_test(self, input: str, output: str):
        file = File(parse(input))
        encoded = encode_main_constraint(file)

        self.assertEqual(output, repr(encoded))
