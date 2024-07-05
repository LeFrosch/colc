import typing

from colc.common import TextFile, fatal_problem
from colc.frontend import ast


class File:
    def __init__(self, source: TextFile, includes: list['File'], definitions: list[ast.Definition]):
        self.source = source
        self.includes = includes
        self.definitions = definitions

    @property
    def mappings(self) -> list[ast.MDefinition]:
        return [it for it in self.definitions if isinstance(it, ast.MDefinition)]

    def _resolve(self, subtype: type, name: str) -> typing.Optional[ast.Definition]:
        frontier: list[File] = [self]

        while len(frontier) > 0:
            file = frontier.pop()
            frontier.extend(file.includes)

            for definition in file.definitions:
                if isinstance(definition, subtype) and definition.identifier.name == name:
                    return definition

        return None

    def constraint_type(self, identifier: ast.Identifier) -> ast.CDefinitionType:
        definition = self._resolve(ast.CDefinitionType, identifier.name)

        if definition is None:
            fatal_problem('undefined identifier', identifier)

        return typing.cast(ast.CDefinitionType, definition)

    def constraint_main(self) -> ast.CDefinitionMain:
        definition = self._resolve(ast.CDefinitionMain, 'main')

        if definition is None:
            fatal_problem('undefined main constraint')

        return typing.cast(ast.CDefinitionMain, definition)

    def predicate(self, identifier: ast.Identifier) -> ast.PDefinition:
        definition = self._resolve(ast.PDefinition, identifier.name)

        if definition is None:
            fatal_problem('undefined identifier', identifier)

        return typing.cast(ast.PDefinition, definition)
