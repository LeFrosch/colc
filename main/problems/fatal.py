import dataclasses
import typing

import lark

from .string_builder import StringBuilder


@dataclasses.dataclass
class SourceLocation:
    line: int
    column: int
    length: int


def location_from_token(token: lark.Token) -> SourceLocation:
    return SourceLocation(
        line=token.line,
        column=token.column,
        length=len(str(token))
    )


def location_from_pos(line: int, column: int) -> SourceLocation:
    return SourceLocation(
        line=line,
        column=column,
        length=1,
    )


class FatalProblem(Exception):
    """
    Raised in case of fatal problem. Should only be raised in the case of unrecoverable input error.
    """

    def __init__(self, message: str, location: SourceLocation | None):
        super().__init__(message)
        self.location = location

    def _render_marker(self, sb: StringBuilder, text: str):
        if self.location is None:
            return
        lines = text.splitlines()

        if self.location.line <= 0 or self.location.line > len(lines):
            return
        line = lines[self.location.line - 1]

        if self.location.column < 0 or self.location.column > len(line):
            return
        column = self.location.column - 1
        length = min(len(line) - column, max(1, self.location.length))

        marker = ' ' * column + '^' * length

        sb.write_line('>> ' + line)
        sb.write_line('>> ' + marker)

    def render(self, text: str) -> str:
        sb = StringBuilder()

        self._render_marker(sb, text)
        sb.write_line(f'fatal problem: {str(self)}')

        return sb.build()


def report_fatal(message: str, location: SourceLocation | None = None) -> typing.NoReturn:
    raise FatalProblem(message, location)
