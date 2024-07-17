import dataclasses
import abc
from typing import Protocol, Any, cast, Optional

from colc.common import fatal_problem, internal_problem, Value, RuntimeValue, ComptimeValue, Type, first, types
from colc.frontend import Operator, Comparison, ast

from ._instruction import Opcode
from ._file import File


@dataclasses.dataclass
class Function(abc.ABC):
    name: str
    parameters: list[Type]
    returns: Type

    @abc.abstractmethod
    def comptime(self, *args: Any) -> Optional[ComptimeValue]: ...


class ComptimeImpl(Protocol):
    def __call__(self, *args: Any) -> Any: ...


@dataclasses.dataclass
class BuiltinFunction(Function):
    opcode: Opcode
    comptime_impl: ComptimeImpl

    def comptime(self, *args: Any) -> Optional[ComptimeValue]:
        result = self.comptime_impl(*args)
        if result is None:
            return None

        return ComptimeValue.from_python(result)


@dataclasses.dataclass
class DefinedFunction(Function):
    definition: ast.FDefinition

    def comptime(self, *args: Any) -> Optional[ComptimeValue]:
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
                returns=Type.from_python(annotations['return']),
                opcode=opcode,
                comptime_impl=func,
            )
        )

        return func

    return decorator


def operator_unary_infer(op: Operator, value: Value) -> RuntimeValue:
    return_types = [
        it.returns
        for it in _builtins
        if it.name == op and len(it.parameters) == 1 and it.parameters[0].compatible(value.type)
    ]

    if len(return_types) == 0:
        fatal_problem(f'undefined operator {op} {value.type}', op)

    return RuntimeValue(Type.lup(return_types))


def operator_binary_infer(op: Operator, left: Value, right: Value) -> RuntimeValue:
    return_types = [
        it.returns
        for it in _builtins
        if it.name == op
        and len(it.parameters) == 2
        and it.parameters[0].compatible(left.type)
        and it.parameters[1].compatible(right.type)
    ]

    if len(return_types) == 0:
        fatal_problem(f'undefined operator {left.type} {op} {right.type}', op)

    return RuntimeValue(Type.lup(return_types))


def comparison_infer(comp: Comparison, left: Value, right: Value) -> RuntimeValue:
    return operator_binary_infer(cast(Operator, comp), left, right)


def operator_unary_evaluate(op: Operator, value: ComptimeValue) -> ComptimeValue:
    candidates = [
        it for it in _builtins if it.name == op and len(it.parameters) == 1 and it.parameters[0].compatible(value.type)
    ]

    if len(candidates) == 0:
        fatal_problem(f'undefined operator {op} {value.type}', op)
    if len(candidates) != 1:
        internal_problem(f'ambiguous operator {op} {value.type}')

    result = candidates[0].comptime(value.comptime)
    if result is None:
        internal_problem(f'cannot resolve operator at comptime {op}')

    return result


def operator_binary_evaluate(op: Operator, left: ComptimeValue, right: ComptimeValue) -> ComptimeValue:
    candidates = [
        it
        for it in _builtins
        if it.name == op
        and len(it.parameters) == 2
        and it.parameters[0].compatible(left.type)
        and it.parameters[1].compatible(right.type)
    ]

    if len(candidates) == 0:
        fatal_problem(f'undefined operator {left.type} {op} {right.type}', op)
    if len(candidates) != 1:
        internal_problem(f'ambiguous operator {left.type} {op} {right.type}')

    try:
        result = candidates[0].comptime(left.comptime, right.comptime)
        if result is None:
            internal_problem(f'cannot resolve operator at comptime {op}')

        return result
    except ArithmeticError:
        fatal_problem(f'arithmetic error: {left.comptime} {op} {right.comptime}', op)


def resolve_function(file: File, identifier: ast.Identifier) -> Function:
    builtin = first(it for it in _builtins if it.name == identifier.name)
    if builtin is not None:
        return builtin

    definition = file.function(identifier)

    # TODO: if function type hints are ever supported, add them here
    return DefinedFunction(
        name=definition.identifier.name,
        parameters=[types.ANY for _ in definition.parameters],
        returns=types.ANY,
        definition=definition,
    )
