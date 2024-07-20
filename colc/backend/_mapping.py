import dataclasses


@dataclasses.dataclass
class Mapping:
    name: str
    labels: list[int]
    code: bytes
