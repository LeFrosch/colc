import dataclasses
import typing

import lark

from .string_builder import StringBuilder


@dataclasses.dataclass
class SourceLocation:
    line: int
    column: int
    length: int


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
        length = len(line) - column

        if self.location.length > 0:
            length = min(len(line) - column, self.location.length)

        marker = ' ' * column + '^' * length

        sb.write_line('>> ' + line)
        sb.write_line('>> ' + marker)

    def render(self, text: str) -> str:
        sb = StringBuilder()

        line = ''
        if self.location is not None:
            line = f' @ line {self.location.line}'

        self._render_marker(sb, text)
        sb.write_line(f'fatal problem: {str(self)}{line}')

        return sb.build()


def fatal(
        message: str,
        at_token: typing.Optional[lark.Token] = None,
        at_pos: typing.Optional[typing.Tuple[int, int]] = None,
) -> typing.NoReturn:
    location = None

    if at_token is not None:
        assert at_token.line == at_token.end_line

        location = SourceLocation(
            line=at_token.line,
            column=at_token.column,
            length=len(str(at_token))
        )

    if at_pos is not None:
        location = SourceLocation(
            line=at_pos[0],
            column=at_pos[1],
            length=1,
        )

    raise FatalProblem(message, location)
