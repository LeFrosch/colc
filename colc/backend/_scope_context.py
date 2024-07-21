from colc.common import Type

from ._instruction import Label


class Context:
    pass


class Function(Context):
    def __init__(self, name: str):
        self._returns: list[Type] = []
        self._end = Label(name)

    @property
    def is_root(self) -> bool:
        return False

    @property
    def end(self):
        return self._end

    def add_return(self, type: Type) -> Label:
        self._returns.append(type)
        return self._end

    def get_return(self) -> Type:
        return Type.lup(self._returns)


class Root(Function):
    def __init__(self):
        super().__init__('root')

    @property
    def is_root(self) -> bool:
        return True


class Loop(Context):
    def __init__(self):
        self._start = Label('start')
        self._end = Label('end')

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end
