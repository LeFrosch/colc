import typing

from colc.common import TextFile, fatal_problem
from colc.frontend import ast


class Pool:
    def __init__(self):
        self.__elements = []

    def intern(self, value) -> int:
        if value in self.__elements:
            return self.__elements.index(value)
        else:
            self.__elements.append(value)
            return len(self.__elements) - 1

    def resolve(self, index: int):
        return self.__elements[index]


class File:
    def __init__(self, source: TextFile, includes: list['File'], definitions: list[ast.Definition]):
        self.source = source
        self.includes = includes
        self.definitions = definitions

    def _resolve[T](self, predicate: typing.Callable[[T], bool]) -> typing.Optional[T]:
        frontier = [self]

        while len(frontier) > 0:
            file = frontier.pop()
            frontier.extend(file.includes)

            for definition in file.definitions:
                if predicate(definition):
                    return definition

        return None

    def constraint_type(self, identifier: ast.Identifier) -> ast.CDefinitionType:
        definition = self._resolve(
            lambda it: isinstance(it, ast.CDefinitionType) and it.identifier.name == identifier.name
        )

        if definition is None:
            fatal_problem('undefined identifier', identifier)

        return definition

    def constraint_main(self) -> ast.CDefinitionMain:
        definition = self._resolve(lambda it: isinstance(it, ast.CDefinitionMain))

        if definition is None:
            fatal_problem('undefined main constraint')

        return definition

    def predicate(self, identifier: ast.Identifier) -> ast.PDefinition:
        definition = self._resolve(lambda it: isinstance(it, ast.PDefinition) and it.identifier.name == identifier.name)

        if definition is None:
            fatal_problem('undefined identifier', identifier)

        return definition

    def intern_constant(self, constant: int | str) -> int:
        return 0
