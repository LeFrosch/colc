import typing

from colc.common import internal_problem
from colc.frontend import Type

CompiletimeValue = str | int


def type_from_value(value: typing.Any) -> Type:
    if isinstance(value, Type):
        return value
    if isinstance(value, str):
        return Type.STRING
    if isinstance(value, int):
        return Type.INTEGER

    internal_problem(f'cannot determine type of {value}')


def assignable_to(type: Type, value: CompiletimeValue) -> bool:
    return type == type_from_value(value)
