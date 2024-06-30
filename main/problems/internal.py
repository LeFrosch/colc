import typing

from .string_builder import StringBuilder


class InternalProblem(Exception):
    """
    Raised in case of an internal problem. Should only be raised in the case of unexpected errors.
    """

    def __init__(self, message: str, cause: Exception | None = None):
        super().__init__(message)
        self.cause = cause

    def render(self) -> str:
        sb = StringBuilder()

        if self.cause:
            sb.write_stacktrace(self.cause)
        else:
            sb.write_stacktrace(self)

        sb.write_line()
        sb.write_line(f'internal problem: {str(self)}')

        return sb.build()


def report_internal(message: str, cause: Exception | None = None) -> typing.NoReturn:
    raise InternalProblem(message, cause)
