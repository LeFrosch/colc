# 1 byte fixpoint numbers with 3 bits for the fraction
_factor = 1 << 3


def fixpoint_can_convert(value: float) -> bool:
    fixpoint = fixpoint_from_float(value)

    return 0 <= fixpoint <= 255 and fixpoint == value * _factor


def fixpoint_from_float(value: float) -> int:
    return int(value * _factor)


def fixpoint_to_float(value: int) -> float:
    return value / _factor
