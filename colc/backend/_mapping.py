import dataclasses

from ._instruction import Instruction


@dataclasses.dataclass
class Mapping:
    name: str
    labels: list[int]
    code: list[Instruction]
