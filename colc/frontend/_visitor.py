import typing

from . import _ast as ast


class Visitor:
    def accept(self, node: ast.Node | None) -> typing.Any:
        if node:
            return getattr(self, node.rule)(node)
        else:
            return None

    def accept_all(self, nodes: typing.Collection[ast.Node | None]) -> list[typing.Any]:
        return [self.accept(it) for it in nodes]
