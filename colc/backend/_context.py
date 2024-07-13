from colc.common import internal_problem, ComptimeValue, ComptimePyType

from ._file import File
from ._config import Config


def check_const_pool_value(value: ComptimePyType) -> int | str:
    if value is None:
        internal_problem('cannot intern none')
    if isinstance(value, bool):
        internal_problem('cannot intern bool')

    return value


class Context:
    def __init__(self, config: Config, file: File):
        self.config = config
        self.file = file

        # allow assignments of none, compilation should fail
        self._const_pool: list[ComptimePyType] = []

    def intern_const(self, value: ComptimeValue | ComptimePyType) -> int:
        if isinstance(value, ComptimeValue):
            value = value.comptime

        if value in self._const_pool:
            return self._const_pool.index(value)
        else:
            self._const_pool.append(value)
            return len(self._const_pool) - 1

    def get_const_pool(self) -> list[int | str]:
        return [check_const_pool_value(it) for it in self._const_pool]
