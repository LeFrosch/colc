import traceback


class StringBuilder:
    def __init__(self):
        self._buffer = []

    def write_line(self, line: str = ''):
        self._buffer.append(line)

    def write_stacktrace(self, exception: Exception):
        self._buffer.append(traceback.format_tb(exception.__traceback__))

    def build(self) -> str:
        return '\n'.join(self._buffer)
