import pathlib

from ._text import TextFile
from ._fatal import fatal_problem


def read_file(path: pathlib.Path | str) -> TextFile:
    if not isinstance(path, pathlib.Path):
        path = pathlib.Path(path)

    try:
        return TextFile(path, path.read_text())
    except IOError:
        fatal_problem(f'could not read file {path}')


def write_file(path: pathlib.Path | str, data: bytes):
    if not isinstance(path, pathlib.Path):
        path = pathlib.Path(path)

    try:
        print(f'data size: {len(data)}')
        path.write_bytes(data)
    except IOError:
        fatal_problem(f'could not write file {path}')
