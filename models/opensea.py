from dataclasses import dataclass


@dataclass
class FloorPrice:
    source: str
    project: str
    price: str
