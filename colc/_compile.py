import pathlib
import lark

from colc.common import TextFile, fatal_problem
from colc.backend import File, process_constraint
from colc.frontend import parse, ast

from .object import Object

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
    return parse_file(_read_file(_find_include(include)))


def _read_file(path: pathlib.Path) -> TextFile:
    try:
        return TextFile(path, path.read_text())
    except IOError:
        fatal_problem(f'could not read file {path}')


def parse_file(file: TextFile) -> File:
    try:
        result = parse(file)
    except lark.UnexpectedToken as e:
        if e.token.type == '$END':
            fatal_problem('unexpected end of input')
        else:
            fatal_problem('unexpected token', file.location_from_token(e.token))
    except lark.UnexpectedCharacters as e:
        fatal_problem('unexpected character', file.location_from_position(e.line - 1, e.column - 1))
    except lark.UnexpectedEOF:
        fatal_problem('unexpected end of input')

    includes = [_parse_include(it) for it in result if isinstance(it, ast.Include)]
    definitions = [it for it in result if isinstance(it, ast.Definition)]

    return File(file, includes, definitions)


def compile_file(file: TextFile) -> Object:
    parsed = parse_file(file)

    constraint = process_constraint(parsed)

    return Object(constraint)
