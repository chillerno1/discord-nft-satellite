from dataclasses import dataclass


@dataclass
class NFTPrice:
    source: str
    project: str
    price: str
