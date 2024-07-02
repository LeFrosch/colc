from colc.frontend import Node

from .file import File
from .object import Object
from .process_constraints import process_constraint


def process(definitions: list[Node]) -> Object:
    file = File(definitions)

    constraint = process_constraint(file)

    return Object(constraint)
