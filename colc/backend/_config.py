import enum
from typing import Tuple, Optional

from colc.common import fatal_problem


class Optimization(enum.StrEnum):
    REDUNDANT_QUANTIFIER = 'redundant-quantifier'


def _parse(flag: str) -> Tuple[str, bool]:
    if flag.startswith('no-'):
        return flag[3:], False
    else:
        return flag, True


class Config:
    def __init__(self, optimizations: Optional[list[str]] = None):
        self._optimizations: set[str] = set(Optimization)

        for flag in filter(str.strip, optimizations or []):
            if flag == 'all':
                self._optimizations = set(Optimization)
                continue

            if flag == 'none':
                self._optimizations = set()
                continue

            flag, enabled = _parse(flag)
            if flag not in Optimization:
                fatal_problem(f'unknown optimization {flag}')

            if enabled:
                self._optimizations.add(flag)
            else:
                self._optimizations.discard(flag)

    def enabled(self, optimization: Optimization) -> bool:
        return optimization in self._optimizations
