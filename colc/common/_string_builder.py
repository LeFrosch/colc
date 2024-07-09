import traceback


class StringBuilder:
    def __init__(self):
        self._buffer: list[str] = []

    def write_line(self, line: str = ''):
        self._buffer.append(line)

    def write_stacktrace(self, exception: Exception):
        self._buffer.extend(traceback.format_tb(exception.__traceback__))

    def build(self) -> str:
        return '\n'.join(self._buffer)
