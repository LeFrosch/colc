from typing import Optional, NoReturn

from ._string_builder import StringBuilder


class InternalProblem(Exception):
    """
    Raised in case of an internal problem. Should only be raised in the case of unexpected errors.
    """

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.cause = cause

    def render(self) -> str:
        sb = StringBuilder()

        if self.cause is not None:
            sb.write_stacktrace(self.cause)
            sb.write_line()
            sb.write_line(f'internal problem: {str(self)} - {self.cause.__class__.__name__}')
        else:
            sb.write_stacktrace(self)
            sb.write_line()
            sb.write_line(f'internal problem: {str(self)}')

        return sb.build()


def internal_problem(message: str, cause: Optional[Exception] = None) -> NoReturn:
    if isinstance(cause, InternalProblem):
        raise cause
    else:
        raise InternalProblem(message, cause)
