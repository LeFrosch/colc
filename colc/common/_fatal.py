import dataclasses
import typing

from ._text import Location
from ._string_builder import StringBuilder


@dataclasses.dataclass
class SourceLocation:
    line: int
    column: int
    length: int


class FatalProblem(Exception):
    """
    Raised in case of fatal problem. Should only be raised in the case of unrecoverable input error.
    """

    def __init__(self, message: str, locations: list[Location]):
        super().__init__(message)
        self.locations = locations

    def _render_location(self, sb: StringBuilder, range: Location):
        text = range.file.text

        start = range.start_position
        end = range.end_position

        # TODO: support multi-line ranges
        assert start.line == end.line

        line = text.splitlines()[start.line]
        length = max(1, end.column - start.column)
        marker = ' ' * start.column + '^' * length

        sb.write_line(f'{range.file.path} @ line {start.line + 1}')
        sb.write_line('>> ' + line)
        sb.write_line('>> ' + marker)

    def render(self) -> str:
        sb = StringBuilder()

        for range in self.locations:
            self._render_location(sb, range)

        sb.write_line(f'fatal problem: {str(self)}')

        return sb.build()


def fatal_problem(message: str, *args) -> typing.NoReturn:
    locations = [it if isinstance(it, Location) else it.location for it in args]
    raise FatalProblem(message, locations)
