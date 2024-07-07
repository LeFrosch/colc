from ._file import File


class Context:
    def __init__(self, file: File):
        self.file = file
        self.const_pool: list[str | int] = []

    def intern_const(self, value: str | int) -> int:
        if value in self.const_pool:
            return self.const_pool.index(value)
        else:
            self.const_pool.append(value)
            return len(self.const_pool) - 1
