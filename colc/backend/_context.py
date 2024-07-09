from colc.frontend import ComptimeValue

from ._file import File
from ._config import Config


class Context:
    def __init__(self, config: Config, file: File):
        self.config = config
        self.file = file
        self.const_pool: list[int | str] = []

    def intern_const(self, value: int | str | ComptimeValue) -> int:
        if isinstance(value, ComptimeValue):
            value = value.comptime

        if value in self.const_pool:
            return self.const_pool.index(value)
        else:
            self.const_pool.append(value)
            return len(self.const_pool) - 1
