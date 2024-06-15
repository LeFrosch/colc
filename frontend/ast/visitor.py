import typing

from .nodes import ASTNode


class Visitor:
    def accept(self, node: ASTNode | None) -> typing.Any:
        if node:
            return getattr(self, node.rule)(node)
        else:
            return None

    def accept_all(self, nodes: list[ASTNode | None]) -> list[typing.Any]:
        return [self.accept(it) for it in nodes]
