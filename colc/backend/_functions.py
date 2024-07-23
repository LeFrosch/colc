import dataclasses
from typing import Protocol, Any, cast, Optional

from colc.common import (
    fatal_problem,
    internal_problem,
    Value,
    RuntimeValue,
    ComptimeValue,
    Type,
    first,
    types,
    comptime,
)
from colc.frontend import Operator, Comparison, ast

from ._opcode import Opcode
from ._file import File


@dataclasses.dataclass
class Function:
    name: str
    parameters: list[Type]
    returns: Type


class ComptimeImpl(Protocol):
    def __call__(self, *args: comptime) -> Optional[comptime]: ...


@dataclasses.dataclass
class BuiltinFunction(Function):
    opcode: Opcode
    comptime: ComptimeImpl


@dataclasses.dataclass
class DefinedFunction(Function):
    definition: ast.FDefinition

    def comptime(self, *args: Any) -> Optional[comptime]:
        return None


_builtins: list[BuiltinFunction] = []


def builtin(name: str, opcode: Opcode):
    def decorator(func):
        param_names = func.__code__.co_varnames
        annotations = func.__annotations__

        _builtins.append(
            BuiltinFunction(
                name=name,
                parameters=[Type.from_python(annotations[it]) for it in param_names],
                returns=Type.from_python(annotations.get('return')),
                opcode=opcode,
                comptime=func,
            )
        )

        return func

    return decorator


def _operator_find(name: str, n_params: int) -> BuiltinFunction:
    operator = first(it for it in _builtins if it.name == name and len(it.parameters) == n_params)

    if operator is None:
        internal_problem(f'undefined operator: {name}')

    return operator


def _operator_unary_find_compatible(op: Operator, value: Type) -> BuiltinFunction:
    operator = _operator_find(op, 1)

    if len(operator.parameters) != 1:
        internal_problem(f'invalid unary operator: {op}')
    if not operator.parameters[0].compatible(value):
        fatal_problem(f'undefined operator {op} {value}', op)

    return operator


def _operator_binary_find_compatible(op: Operator, left: Type, right: Type) -> BuiltinFunction:
    operator = _operator_find(op, 2)

    if len(operator.parameters) != 2:
        internal_problem(f'invalid binary operator: {op}')

    # prepend is special because return type depends on operands
    if op == Operator.PREPEND:
        if left.is_list or not right.is_list:
            fatal_problem(f'undefined operator {left} {op} {right}', op)
    else:
        if not operator.parameters[0].compatible(left) or not operator.parameters[1].compatible(right):
            fatal_problem(f'undefined operator {left} {op} {right}', op)

    return operator


def operator_unary_infer(op: Operator, value: Value) -> RuntimeValue:
    return RuntimeValue(_operator_unary_find_compatible(op, value.type).returns)


def operator_binary_infer(op: Operator, left: Value, right: Value) -> RuntimeValue:
    operator = _operator_binary_find_compatible(op, left.type, right.type)

    # prepend is special create new return type depending on operands
    if op == Operator.PREPEND:
        return RuntimeValue(Type(left.type.values | right.type.values, list=True))
    else:
        return RuntimeValue(operator.returns)


def comparison_infer(comp: Comparison, left: Value, right: Value) -> RuntimeValue:
    return operator_binary_infer(cast(Operator, comp), left, right)


def operator_unary_evaluate(op: Operator, value: ComptimeValue) -> ComptimeValue:
    operator = _operator_unary_find_compatible(op, value.type)
    inferred = operator_unary_infer(op, value).type

    result = operator.comptime(value.data)
    if result is None:
        internal_problem(f'cannot resolve operator at comptime {op}')

    return ComptimeValue(result, type=inferred)


def operator_binary_evaluate(op: Operator, left: ComptimeValue, right: ComptimeValue) -> ComptimeValue:
    operator = _operator_binary_find_compatible(op, left.type, right.type)
    inferred = operator_binary_infer(op, left, right).type

    try:
        result = operator.comptime(left.data, right.data)
        if result is None:
            internal_problem(f'cannot resolve operator at comptime {op}')

        return ComptimeValue(result, type=inferred)
    except ArithmeticError:
        fatal_problem(f'arithmetic error: {left.data} {op} {right.data}', op)


def resolve_function(file: File, identifier: ast.Identifier) -> Function:
    function = first(it for it in _builtins if it.name == identifier.name)
    if function is not None:
        return function

    definition = file.function(identifier)

    # TODO: if function type hints are ever supported, add them here
    return DefinedFunction(
        name=definition.identifier.name,
        parameters=[types.ANY for _ in definition.parameters],
        returns=types.ANY,
        definition=definition,
    )
