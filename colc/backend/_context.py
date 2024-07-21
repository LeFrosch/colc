from typing import Optional

from colc.common import internal_problem, ComptimeValue, num, comptime

from ._file import File
from ._config import Config
from ._utils import Pool


def check_const_pool_value(value: comptime) -> num | str:
    if value is None:
        internal_problem('cannot intern none')
    if isinstance(value, bool):
        internal_problem('cannot intern bool')
    if isinstance(value, list):
        internal_problem('cannot intern list')

    return value


class Context:
    def __init__(self, config: Config, file: File):
        self.config = config
        self.file = file

        # allow assignments of none, compilation should fail
        self._const_pool = Pool[comptime]()
        self._label_pool = Pool[str]()

    def intern_const(self, value: ComptimeValue | comptime) -> int:
        if isinstance(value, ComptimeValue):
            value = value.data
        return self._const_pool.intern(value)

    def get_const_pool(self) -> list[num | str]:
        return [check_const_pool_value(it) for it in self._const_pool]

    def intern_label(self, label: str) -> int:
        return self._label_pool.intern(label)

    def lookup_label(self, label: str) -> Optional[int]:
        return self._label_pool.lookup(label)
