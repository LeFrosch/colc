import re


def to_snake_case(name):
    """
    Converts a name from camelCase to snake_case.
    Source: https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
