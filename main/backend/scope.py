from frontend.ast import Parameter


class Scope:
    def __init__(self):
        self._declarations = {}

    def declare(self, key: str, value):
        self._declarations[key] = value

    def lookup(self, key: str):
        return self._declarations[key]

    @staticmethod
    def from_call(parameters: list[Parameter], arguments: list) -> 'Scope':
        # TODO: length and type check

        scope = Scope()
        for (param, arg) in zip(parameters, arguments):
            scope.declare(param.identifier, arg)

        return scope
