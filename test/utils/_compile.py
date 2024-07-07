import pathlib
from typing import Tuple

from colc import TextFile, parse_file, LExpression, Instruction, Object
from colc.backend import Context, process_constraint, process_mappings


def create_test_file(text: str) -> TextFile:
    return TextFile(pathlib.Path('test.col'), text)


def compile_constraint(text: str) -> Tuple[Context, LExpression]:
    file = create_test_file(text)
    ctx = Context(parse_file(file))

    return ctx, process_constraint(ctx)


def compile_mappings(text: str) -> Tuple[Context, dict[str, list[Instruction]]]:
    file = create_test_file(text)
    ctx = Context(parse_file(file))

    return ctx, process_mappings(ctx)


def compile_object(text: str) -> Tuple[Context, Object]:
    file = create_test_file(text)
    ctx = Context(parse_file(file))

    return ctx, Object(
        ctx=ctx,
        constraint=process_constraint(ctx),
        mappings=process_mappings(ctx),
    )
