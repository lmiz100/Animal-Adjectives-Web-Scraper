from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AnimalEntry:
    name: str
    collateral_adjectives: List[str]
    href: str
    image_path: Optional[str] = None
