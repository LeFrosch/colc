from typing import Optional

from colc.common import internal_problem, ComptimeValue, ComptimePyType

from ._file import File
from ._config import Config
from ._utils import Pool


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
        self._const_pool = Pool[ComptimePyType]()
        self._label_pool = Pool[str]()

    def intern_const(self, value: ComptimeValue | ComptimePyType) -> int:
        if isinstance(value, ComptimeValue):
            value = value.comptime
        return self._const_pool.intern(value)

    def get_const_pool(self) -> list[int | str]:
        return [check_const_pool_value(it) for it in self._const_pool]

    def intern_label(self, label: str) -> int:
        return self._label_pool.intern(label)

    def lookup_label(self, label: str) -> Optional[int]:
        return self._label_pool.lookup(label)
