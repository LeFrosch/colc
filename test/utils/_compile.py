import pathlib

from colc import TextFile, parse_file, LExpression, Instruction, compile_file, Object
from colc.backend import Context, process_constraint, process_mappings


def create_test_file(text: str) -> TextFile:
    return TextFile(pathlib.Path('test.col'), text)


def compile_constraint(text: str) -> LExpression:
    file = create_test_file(text)
    ctx = Context(parse_file(file))

    return process_constraint(ctx)


def compile_mappings(text: str) -> dict[str, list[Instruction]]:
    file = create_test_file(text)
    ctx = Context(parse_file(file))

    return process_mappings(ctx)


def compile_object(text: str) -> Object:
    file = create_test_file(text)
    return compile_file(file)
