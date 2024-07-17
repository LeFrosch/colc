from .__about__ import __version__

from colc.common import num
from colc.backend import LExpression, Mapping, Context


class Object:
    version: str

    # main constraint
    constraint: LExpression

    # shared pool of constant definitions
    const_pool: list[str | num]

    # list of available mappings
    mappings: list[Mapping]

    def __init__(self, ctx: Context, constraint: LExpression, mappings: list[Mapping]):
        self.version = __version__
        self.constraint = constraint
        self.mappings = mappings
        self.const_pool = ctx.get_const_pool()
