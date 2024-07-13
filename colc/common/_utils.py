import re
from typing import TypeVar, Iterable, Optional, Protocol


def to_snake_case(name):
    """
    Converts a name from camelCase to snake_case.
    Source: https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


T = TypeVar('T', covariant=True)


def flatten(xss: Iterable[Iterable[T]]) -> Iterable[T]:
    return (x for xs in xss for x in xs)


class SupportsIter(Protocol[T]):
    def __iter__(self) -> T: ...


def first(xs: SupportsIter) -> Optional[T]:
    return next(iter(xs), None)
