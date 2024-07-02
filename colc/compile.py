import pathlib
import lark

from colc import problems
from colc.backend import File, process_constraint
from colc.frontend import TextFile, parse, Include, Definition, Location

from .object import Object

_includes = pathlib.Path(__file__).parent.joinpath('includes')


def _find_include(include: Include) -> pathlib.Path:
    path = pathlib.Path(include.path.value + '.coli')

    if path.exists():
        return path

    if path.is_absolute():
        problems.fatal(f'could not locate include', include.path)

    # TODO: support custom include dirs
    path = _includes.joinpath(path)

    if path.exists():
        return path

    problems.fatal(f'could not locate include', include.path)


def _parse_include(include: Include) -> File:
    return parse_file(_read_file(_find_include(include)))


def _read_file(path: pathlib.Path) -> TextFile:
    try:
        return TextFile(path, path.read_text())
    except IOError:
        problems.fatal(f'could not read file {path}')


def parse_file(file: TextFile) -> File:
    try:
        result = parse(file)
    except lark.UnexpectedToken as e:
        if e.token.type == '$END':
            problems.fatal('unexpected end of input')
        else:
            problems.fatal('unexpected token', file.location_from_token(e.token))
    except lark.UnexpectedCharacters as e:
        problems.fatal('unexpected character', file.location_from_position(e.line - 1, e.column - 1))
    except lark.UnexpectedEOF:
        problems.fatal('unexpected end of input')
    except Exception as e:
        problems.internal('unexpected lark exception')

    includes = [_parse_include(it) for it in result if isinstance(it, Include)]
    definitions = [it for it in result if isinstance(it, Definition)]

    return File(file, includes, definitions)


def compile_file(file: TextFile) -> Object:
    parsed = parse_file(file)

    constraint = process_constraint(parsed)

    return Object(constraint)
