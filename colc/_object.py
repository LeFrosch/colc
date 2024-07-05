from .__about__ import __version__

from colc.backend import LExpression


class Object:
    version: str
    constraint: LExpression

    def __init__(self, constraint: LExpression):
        self.version = __version__
        self.constraint = constraint
