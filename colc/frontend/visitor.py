import typing

from .ast import Node


class Visitor:
    def accept(self, node: Node | None) -> typing.Any:
        if node:
            return getattr(self, node.rule)(node)
        else:
            return None

    def accept_all(self, nodes: list[Node | None]) -> list[typing.Any]:
        return [self.accept(it) for it in nodes]
