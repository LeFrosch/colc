import typing

from colc import problems
from colc.frontend import CDefinitionType, CDefinitionMain, PDefinition, Definition, TextFile, Identifier


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
    def __init__(self, source: TextFile, includes: list['File'], definitions: list[Definition]):
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

    def constraint_type(self, identifier: Identifier) -> CDefinitionType:
        definition = self._resolve(
            lambda it: isinstance(it, CDefinitionType) and it.identifier.name == identifier.name
        )

        if definition is None:
            problems.fatal('undefined identifier', identifier)

        return definition

    def constraint_main(self) -> CDefinitionMain:
        definition = self._resolve(lambda it: isinstance(it, CDefinitionMain))

        if definition is None:
            problems.fatal('undefined main constraint')

        return definition

    def predicate(self, identifier: Identifier) -> PDefinition:
        definition = self._resolve(
            lambda it: isinstance(it, PDefinition) and it.identifier.name == identifier.name
        )

        if definition is None:
            problems.fatal('undefined identifier', identifier)

        return definition

    def intern_constant(self, constant: int | str) -> int:
        return 0

