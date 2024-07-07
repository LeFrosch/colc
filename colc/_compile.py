import pathlib

from colc.common import TextFile, fatal_problem, read_file
from colc.backend import File, Context, process_constraint, process_mappings
from colc.frontend import parse, ast

from ._object import Object

_includes = pathlib.Path(__file__).parent.joinpath('includes')


def _find_include(include: ast.Include) -> pathlib.Path:
    path = pathlib.Path(include.path.value + '.coli')

    if path.exists():
        return path

    if path.is_absolute():
        fatal_problem('could not locate include', include.path)

    # TODO: support custom include dirs
    path = _includes.joinpath(path)

    if path.exists():
        return path

    fatal_problem('could not locate include', include.path)


def _parse_include(include: ast.Include) -> File:
    return parse_file(read_file(_find_include(include)))


def parse_file(file: TextFile) -> File:
    result = parse(file)

    includes = [_parse_include(it) for it in result if isinstance(it, ast.Include)]
    definitions = [it for it in result if isinstance(it, ast.Definition)]

    return File(file, includes, definitions)


def compile_file(file: TextFile) -> Object:
    ctx = Context(parse_file(file))

    return Object(
        ctx=ctx,
        constraint=process_constraint(ctx),
        mappings=process_mappings(ctx),
    )


def compile(path: str) -> Object:
    return compile_file(read_file(path))
