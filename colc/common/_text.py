import dataclasses
import pathlib

import lark


@dataclasses.dataclass
class TextFile:
    path: pathlib.Path
    text: str

    def location_from_token(self, token: lark.Token) -> 'Location':
        return Location(
            file=self,
            start=token.start_pos,
            end=token.end_pos,
        )

    def location_from_position(self, line: int, column: int) -> 'Location':
        for i, c in enumerate(self.text):
            if c == '\n':
                line -= 1

            if line <= 0:
                return Location(self, i + column, i + column)

        assert False


@dataclasses.dataclass
class Position:
    line: int
    column: int


@dataclasses.dataclass
class Location:
    file: TextFile

    start: int
    end: int

    def _position_for(self, offset: int):
        assert len(self.file.text) >= offset

        line = 0
        column = 0

        for c in self.file.text[0:offset]:
            if c == '\n':
                line += 1
                column = 0
            else:
                column += 1

        return Position(line, column)

    @property
    def start_position(self) -> Position:
        return self._position_for(self.start)

    @property
    def end_position(self) -> Position:
        return self._position_for(self.end)
