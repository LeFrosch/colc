from ._file import File


class Context:
    def __init__(self, file: File):
        self.file = file
        self._const_pool: list[str | int] = []

    def intern_const(self, value: str | int) -> int:
        if value in self._const_pool:
            return self._const_pool.index(value)
        else:
            self._const_pool.append(value)
            return len(self._const_pool) - 1
