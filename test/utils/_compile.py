import pathlib
from typing import Tuple, Optional

from colc import TextFile, parse_file, LExpression, Instruction, Object
from colc.backend import Context, Config, process_constraint, process_mappings


def create_test_context(text: str, config: Optional[Config]) -> Context:
    file = TextFile(pathlib.Path('test.col'), text)
    return Context(config or Config(), parse_file(file))


def compile_constraint(text: str, config: Optional[Config] = None) -> Tuple[Context, LExpression]:
    ctx = create_test_context(text, config)
    return ctx, process_constraint(ctx)


def compile_mappings(text: str, config: Optional[Config] = None) -> Tuple[Context, dict[str, list[Instruction]]]:
    ctx = create_test_context(text, config)
    return ctx, process_mappings(ctx)


def compile_object(text: str, config: Optional[Config] = None) -> Tuple[Context, Object]:
    ctx = create_test_context(text, config)

    return ctx, Object(
        ctx=ctx,
        constraint=process_constraint(ctx),
        mappings=process_mappings(ctx),
    )
