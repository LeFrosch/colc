import dataclasses
from typing import Protocol, Any

from colc.common import fatal_problem, internal_problem
from colc.frontend import Operator, Value, RuntimeValue, ComptimeValue, Type


class EvaluateCallable(Protocol):
    def __call__(self, *args: Any) -> ComptimeValue: ...


@dataclasses.dataclass
class Function:
    name: str
    parameter: list[Type]
    returns: Type
    evaluate: EvaluateCallable


_functions: list[Function] = []


def function(name: str):
    def decorator(func):
        param_names = func.__code__.co_varnames
        annotations = func.__annotations__

        _functions.append(
            Function(
                name=name,
                parameter=[Type.from_python(annotations[it]) for it in param_names],
                returns=Type.from_python(annotations['return']),
                evaluate=lambda *args: ComptimeValue(func(*args)),
            )
        )

        return func

    return decorator


def operator_infer(op: Operator, left: Value, right: Value) -> RuntimeValue:
    return_types = [
        it.returns
        for it in _functions
        if it.name == op
        and len(it.parameter) == 2
        and it.parameter[0] in left.possible_types
        and it.parameter[1] in right.possible_types
    ]

    if len(return_types) == 0:
        fatal_problem(f'undefined operator {left} {op} {right}', op)

    return RuntimeValue(set(return_types))


def operator_evaluate(op: Operator, left: ComptimeValue, right: ComptimeValue) -> ComptimeValue:
    candidates = [
        it
        for it in _functions
        if it.name == op
        and len(it.parameter) == 2
        and it.parameter[0] == left.concrete_type
        and it.parameter[1] == right.concrete_type
    ]

    if len(candidates) == 0:
        fatal_problem(f'undefined operator {left} {op} {right}', op)
    if len(candidates) != 1:
        internal_problem(f'ambiguous operator {left} {op} {right}')

    try:
        return candidates[0].evaluate(left.comptime, right.comptime)
    except ArithmeticError:
        fatal_problem(f'arithmetic error: {left.comptime} {op} {right.comptime}', op)
